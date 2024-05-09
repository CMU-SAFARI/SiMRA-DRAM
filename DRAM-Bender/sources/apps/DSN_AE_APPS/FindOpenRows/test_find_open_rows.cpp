#include "instruction.h"
#include "prog.h"
#include "platform.h"
#include <fstream>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <cstring>
#include <list>
#include <cstdlib>
#include <chrono>
#include "../util.h"
using namespace std;

// hytt00
//#banks: 16, #rows: 32768, #cols:1024
// DQ:x8, SODIMM, #ranks: 1

#define NUM_BANKS 16
//#define NUM_ROWS 300 //32768
#define NUM_COLS 1024

// Stride register ids are fixed and should not be changed
// CASR should always be reg 0
// BASR should always be reg 1
// RASR should always be reg 2
#define CASR 0
#define BASR 1
#define RASR 2
#define LOOP_BANKS 3
#define CAR 4
#define LOOP_ROWS 5
#define RAR 6
#define BAR 7
#define NUM_ROWS_REG 8
#define LOOP_SEGMENT 9
#define RF_REG 10
#define NUM_BANKS_REG 11 //RTHIRD_REG
#define PATTERN_REG 12 
#define LOOP_COLS 13 //RSECOND_REG
#define NUM_COLS_REG 14
#define SEGMENT_REG 15


Program wrRow_after_double_act(int bank_reg, uint32_t wr_pattern)
{
  Program p;

  p.add_inst(SMC_LI(wr_pattern, PATTERN_REG)); // s
  for (int i = 0; i < 16; i++)
    p.add_inst(SMC_LDWD(PATTERN_REG, i));
  p.add_inst(SMC_LI(0, CAR));
  p.add_inst(SMC_LI(0, LOOP_COLS));
  p.add_label("WR_ROW_QUACC");
  p.add_below(WRITE(bank_reg, CAR, 1));
  p.add_inst(SMC_ADDI(LOOP_COLS, 1, LOOP_COLS));
  p.add_branch(p.BR_TYPE::BL, LOOP_COLS, NUM_COLS_REG, "WR_ROW_QUACC");

  return p;
}
int read_args_n_parse(int argc, char* argv[],uint32_t *t_12, uint32_t *t_23,
                      uint32_t *first_subarray_addr, uint32_t *last_subarray_addr, uint32_t *r_first,
                      std::ofstream &out_file)
{
  if(argc != 7)
  {
    printf("Usage: \n ./quac-test <t_12> <t_23> <first_subarray_addr> <last_subarray_addr> <r_first> <out_file>\n");
    return(0);
  }

  *t_12                       = atoi(argv[1]);
  *t_23                       = atoi(argv[2]);
  *first_subarray_addr        = atoi(argv[3]);
  *last_subarray_addr         = atoi(argv[4]);
  *r_first                    = atoi(argv[5]);
  out_file.open(std::string(argv[6]), std::ios::app);
  return 1;
}
Program _init()
{
  Program program;
  program.add_inst(SMC_LI(NUM_BANKS, NUM_BANKS_REG)); // load NUM_BANKS into NUM_BANKS_REG
  program.add_inst(SMC_LI(8, CASR));                  // Load 8 into CASR since each READ reads 8 columns
  program.add_inst(SMC_LI(1, BASR));                  // Load 1 into BASR
  program.add_inst(SMC_LI(1, RASR));                  // Load 1 into RASR
  program.add_inst(SMC_LI(128, NUM_COLS_REG));        // Load COL_SIZE register
  program.add_inst(SMC_LI(0, BAR));
  return program;
}
Program test_prog(uint32_t first_subarray_addr, uint32_t last_subarray_addr, uint32_t t_12, uint32_t t_23, uint32_t r_first, uint32_t wr_pattern)
{
  Program program;
  uint32_t NUM_ROWS = last_subarray_addr - first_subarray_addr;
  program.add_below(_init());
  program.add_inst(all_nops());
  program.add_inst(SMC_LI(r_first+1, LOOP_SEGMENT));
  program.add_label("SEGMENT_LOOP");
  program.add_inst(SMC_LI(NUM_ROWS, NUM_ROWS_REG));
    program.add_inst(SMC_LI(0, LOOP_ROWS));
    program.add_label("WRITE_WHOLE_BANK");
      program.add_below(PRE(BAR, 0, 0));
      program.add_below(wrRow_base_offset(BAR, LOOP_ROWS, first_subarray_addr, ZERO));
      program.add_inst(SMC_ADDI(LOOP_ROWS, 1, LOOP_ROWS));
    program.add_branch(program.BR_TYPE::BL, LOOP_ROWS, NUM_ROWS_REG, "WRITE_WHOLE_BANK");

    program.add_below(PRE(BAR, 0, 0));
    program.add_below(doubleACT_immd_reg(t_12, t_23, r_first, LOOP_SEGMENT));
    program.add_inst(SMC_SLEEP(6));
    program.add_below(wrRow_after_double_act(BAR, wr_pattern));
    program.add_below(PRE(BAR, 0, 0));

    program.add_inst(SMC_LI(0, LOOP_ROWS));
    program.add_label("READ_WHOLE_BANK");  
      program.add_below(rdRow_base_offset(BAR, LOOP_ROWS, first_subarray_addr));
      program.add_inst(all_nops());
      program.add_inst(all_nops());
      program.add_below(PRE(BAR, 0, 0));
      program.add_inst(SMC_ADDI(LOOP_ROWS, 1, LOOP_ROWS));
    program.add_branch(program.BR_TYPE::BL, LOOP_ROWS, NUM_ROWS_REG, "READ_WHOLE_BANK");

    program.add_inst(SMC_ADDI(LOOP_SEGMENT, 1, LOOP_SEGMENT));
    program.add_inst(SMC_LI(last_subarray_addr, NUM_ROWS_REG));   // load NUM_ROWS into NUM_ROWS_REG
  program.add_branch(program.BR_TYPE::BL, LOOP_SEGMENT, NUM_ROWS_REG, "SEGMENT_LOOP");

  program.add_inst(SMC_END());
  return program;
}
void receive_results(SoftMCPlatform &platform, uint32_t r_first, uint32_t first_subarray_addr, uint32_t last_subarray_addr, uint32_t wr_pattern, std::ofstream &out_file)
{
  uint32_t test_pattern = wr_pattern; 
  std::cout << test_pattern;
  long int err_count = 0;
  long int n_err_count = 0;
  uint8_t row[8192];
  for (int r_second = r_first + 1; r_second < last_subarray_addr; r_second++)
  {
    for (int rc = first_subarray_addr; rc < last_subarray_addr; rc++)
    {
      platform.receiveData((void*)row, 8192);
      err_count = 0;
      n_err_count = 0;
      for(int j = 0 ; j < 128 ; j++){
        for (int k = 0 ; k < 64 ; k++){ // each byte in cache line
          uint8_t mini_patt = wr_pattern >> ((uint32_t)(k%4)*8);
          if(mini_patt == (uint8_t)row[j*64 + k]){
            err_count++;
          }
        }
      }
      if (err_count > 0)
      {
        out_file << "\n" << r_first << ",";
        out_file << r_second << ",";
        out_file << rc << ",";
        out_file << std::to_string((float) err_count/8192.0);
      }
    }
  }
  out_file.close();
}
int main(int argc, char*argv[])
{
  //
  SoftMCPlatform platform;
  int err;
  uint32_t t_12, t_23, first_subarray_addr, last_subarray_addr, r_first;
  std::ofstream out_file;

  if(!read_args_n_parse(argc, argv, &t_12, &t_23,
                        &first_subarray_addr, &last_subarray_addr, &r_first,
                        out_file))
  {
    exit(0);
  }
  // Initialize the platform, opens file descriptors for the board PCI-E interface.
  if ((err = platform.init()) != SOFTMC_SUCCESS)
  {
    cerr << "Could not initialize SoftMC Platform: " << err << endl;
  }
  platform.reset_fpga();
  //print arguments
  std::cout << t_12 << ","<< t_23 << ","<< r_first << ","<< first_subarray_addr << ","<< last_subarray_addr;
  std::cout << std::endl;
  
  uint32_t wr_pattern;
  srand(time(NULL)+getpid());
  uint16_t rand1 = (uint16_t) rand();
  wr_pattern = rand1 << 16;
  wr_pattern |= ((uint16_t)rand());
  std::cout << wr_pattern << std::endl;
  
  Program program = test_prog(first_subarray_addr, last_subarray_addr, t_12, t_23, r_first, wr_pattern);
  platform.execute(program);
  receive_results(platform, r_first, first_subarray_addr, last_subarray_addr, wr_pattern, out_file);
  return 0;
}
