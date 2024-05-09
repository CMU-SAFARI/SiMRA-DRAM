#include "instruction.h"
#include "prog.h"
#include "platform.h"
#include <fstream>
#include <iostream>
#include <boost/filesystem.hpp>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <cstring>
#include <list>
#include <cstdlib>
#include <bitset>
#include <math.h> 
#include <iomanip>
#include "../util.h"
using namespace std;


#define NUM_BANKS 1
#define NUM_ROWS 2048 //32768
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
#define ITER_REG 9
#define RF_REG 10
#define NUM_BANKS_REG 11
#define PATTERN_REG 12 
#define LOOP_COLS 13 //R3_REG
#define NUM_COLS_REG 14
#define LOOP_ITER 15

#define ZERO 0x00000000
#define ONE 0xFFFFFFFF

#define DEBUG 0


Program _init(uint32_t bank_id, uint32_t num_iter)
{
  Program program;
  program.add_inst(SMC_LI(NUM_ROWS, NUM_ROWS_REG));   // load NUM_ROWS into NUM_ROWS_REG
  program.add_inst(SMC_LI(NUM_BANKS, NUM_BANKS_REG)); // load NUM_BANKS into NUM_BANKS_REG
  program.add_inst(SMC_LI(num_iter, ITER_REG)); // load NUM_BANKS into NUM_BANKS_REG
  program.add_inst(SMC_LI(8, CASR));                  // Load 8 into CASR since each READ reads 8 columns
  program.add_inst(SMC_LI(1, BASR));                  // Load 1 into BASR
  program.add_inst(SMC_LI(1, RASR));                  // Load 1 into RASR
  program.add_inst(SMC_LI(128, NUM_COLS_REG));        // Load COL_SIZE register
  program.add_inst(SMC_LI(bank_id, BAR));
  return program;

}
Program test_prog(uint32_t num_iter, uint32_t bank_id, 
                  uint32_t n_open_rows, std::vector<uint32_t> &patterns, std::vector<uint32_t> &open_row_idx,
                  uint32_t wr_pattern, 
                  uint32_t r_first, uint32_t r_second,  
                  uint32_t t_12, uint32_t t_23)
{
  Program program;
  program.add_below(_init(bank_id,num_iter));
  srand((unsigned) time(NULL));
  int random = rand();
  program.add_inst(all_nops());
  program.add_inst(all_nops());
  program.add_below(PRE(BAR, 0, 0));
  program.add_inst(SMC_LI(0, LOOP_ITER));
  program.add_label("ITER_LOOP");
    program.add_below(PRE(BAR, 0, 0));
    for(int i = 0; i < n_open_rows; i++)
    {
      random = rand();
      program.add_below(wrRow_immediate_label(BAR, open_row_idx[i], patterns[i],random));
    }
    program.add_inst(SMC_SLEEP(6));
    program.add_below(PRE(BAR, 0, 0));
    program.add_inst(SMC_SLEEP(6));
    program.add_below(wrRow_immediate_label(BAR, r_first, wr_pattern, wr_pattern));
    program.add_inst(SMC_SLEEP(6));
    program.add_below(PRE(BAR, 0, 0));

    program.add_inst(SMC_SLEEP(6));
    program.add_below(doubleACT(t_12, t_23, r_first, r_second));
    program.add_inst(SMC_SLEEP(6));
    program.add_below(PRE(BAR, 0, 0));
    program.add_inst(SMC_SLEEP(6));
    for(int i = 0; i < n_open_rows; i++)
    {
      program.add_below(rdRow_immediate_label(BAR, open_row_idx[i], i));
    }
    program.add_inst(all_nops());
    program.add_inst(all_nops());
    program.add_below(PRE(BAR, 0, 0));
    program.add_inst(all_nops());
    program.add_inst(all_nops());
    program.add_inst(SMC_ADDI(LOOP_ITER, 1, LOOP_ITER));
  program.add_branch(program.BR_TYPE::BL, LOOP_ITER, ITER_REG, "ITER_LOOP");

  program.add_inst(SMC_END());
  return program;
}

void parse_file(std::string file_name, std::vector<uint32_t> &vec)
{
  std::ifstream file;
  file.open(file_name, std::ios::app);
  std::string line;
  while (std::getline(file, line))
  {
    vec.push_back(stol(line));
  }
  file.close();
}
int read_args_n_parse(int argc, char* argv[], 
              uint32_t *r_first, uint32_t *r_second, 
              uint32_t *n_open_rows,
              std::vector<uint32_t> &open_row_idx,
              uint32_t *num_iter, uint32_t *bank_id,
              uint32_t *t_12, uint32_t *t_23, 
              std::ofstream &out_file)
{

  if(argc != 10)
  {
    printf("Usage: \n ./quac-test <inp_pattern_file> <r_frac_idx_file> <r_first> <r_second> <min_row_idx> <max_row_idx> <n_open_rows> <inp_row_file> <num_iter> <bank_id> <maj_x> <t_12> <t_23> <n_frac_times> <t_frac> <out_file>\n");
    return(0); 
  }
  int arg_i = 1;
  //print patterns
  *r_first     = atoi(argv[arg_i++]);
  *r_second    = atoi(argv[arg_i++]);
  *n_open_rows =  atoi(argv[arg_i++]);


  parse_file(std::string(argv[arg_i++]), open_row_idx);
  *num_iter     =  atoi(argv[arg_i++]);
  *bank_id      =  atoi(argv[arg_i++]);
  *t_12         =  atoi(argv[arg_i++]);
  *t_23         =  atoi(argv[arg_i++]);

  out_file.open(std::string(argv[arg_i++]), std::ios::app);

  return 1;
}
void report_coverage_results(SoftMCPlatform &platform, uint32_t wr_pattern,
                            uint32_t bank_id, uint32_t num_iter, vector<uint32_t>& open_row_idx,
                            uint32_t r_first, uint32_t r_second, std::ofstream &out_file,
                            uint32_t *result)
{
  uint8_t row[8192];
  //traverse open rows
  for(int i = 0; i < num_iter; i++)
  {
    for (int rc = 0; rc < open_row_idx.size(); rc++)
    {
      platform.receiveData((void*)row, 8192);
      for(int j = 0 ; j < 128 ; j++){
        for (int k = 0 ; k < 64 ; k++){ // each byte in cache line
          uint8_t mini_patt = wr_pattern >> ((uint32_t)(k%4)*8);
          if(mini_patt == (uint8_t)row[j*64 + k]){
            result[rc]++;
          }
        }
      }
    }
  }


}
std::vector<uint32_t> random_pattern_creator(uint32_t n_open_rows, uint32_t seed)
{
  std::vector<uint32_t> patterns;
  srand((time(NULL)+getpid()+seed));
  for(int i = 0; i < n_open_rows; i++)
  {
    patterns.push_back(rand());
  }
  return patterns;
}

int main(int argc, char*argv[])
{
  SoftMCPlatform platform;
  int err;
  uint32_t r_first,r_second,min_row,max_row,n_open_rows;
  uint32_t num_iter;
  uint32_t bank_id;
  uint32_t maj_x;
  uint32_t t_12;
  uint32_t t_23;
  uint32_t n_frac_times;
  uint32_t t_frac;

  std::vector<uint32_t> r_frac_idx;
  std::vector<uint32_t> open_row_idx;
  std::vector<uint32_t> patterns_old;
  std::ofstream   out_file;



  if(!read_args_n_parse(argc, argv, 
                &r_first, &r_second, 
                &n_open_rows,
                open_row_idx, 
                &num_iter, &bank_id, 
                &t_12, &t_23, 
                out_file))
  {
    exit(0);
  }

  if ((err = platform.init()) != SOFTMC_SUCCESS)
  {
    cerr << "Could not initialize SoftMC Platform: " << err << endl;
  }
  platform.reset_fpga();

  uint32_t zero_result[open_row_idx.size()] {0};
  uint32_t wr_pattern = 0x00000000;
  std::vector<uint32_t> random_patterns = random_pattern_creator(n_open_rows, 0);
  wr_pattern = ZERO;
  Program program = test_prog(num_iter,bank_id, n_open_rows, random_patterns, open_row_idx, 
                              wr_pattern, r_first, r_second, t_12, t_23);
  platform.execute(program);
  report_coverage_results(platform, wr_pattern,
                          bank_id, num_iter, open_row_idx,
                          r_first,  r_second, out_file,
                          zero_result);

  uint32_t one_result[open_row_idx.size()] {0};                       
  wr_pattern = ONE;
  Program program1 = test_prog(num_iter,bank_id, n_open_rows, random_patterns, open_row_idx, 
                              wr_pattern, r_first, r_second, t_12, t_23);
  platform.execute(program1);
  report_coverage_results(platform, wr_pattern,
                          bank_id, num_iter, open_row_idx,
                          r_first,  r_second, out_file,
                          one_result);
  

  uint32_t random_result[open_row_idx.size()] {0};
  srand(time(NULL)+getpid()*r_first*r_second);
  wr_pattern = (uint32_t) rand();
  Program program2 = test_prog(num_iter,bank_id, n_open_rows, random_patterns, open_row_idx, 
                              wr_pattern, r_first, r_second, t_12, t_23);
  platform.execute(program2);
  report_coverage_results(platform, wr_pattern,
                          bank_id, num_iter, open_row_idx,
                          r_first,  r_second, out_file,
                          random_result);
  float avg_result_zero = 0;
  float avg_result_one = 0;
  float avg_result_random = 0;
  for(int i = 0; i < open_row_idx.size(); i++)
  {
    avg_result_zero += (float) zero_result[i]/(8192.0*num_iter);
    avg_result_one += (float) one_result[i]/(8192.0*num_iter);
    avg_result_random += (float) random_result[i]/(8192.0*num_iter);
  }
  avg_result_zero /= open_row_idx.size();
  avg_result_one /= open_row_idx.size();
  avg_result_random /= open_row_idx.size();

  out_file << std::to_string(avg_result_zero) << ",";
  out_file << std::to_string(avg_result_one) << ",";
  out_file << std::to_string(avg_result_random);
  
  out_file.close();
  

  //free memory
  patterns_old.clear();
  open_row_idx.clear();
  random_patterns.clear();

  
  return 0;
}