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

#define HYTT_TIMING 1
#define DEBUG 0

Program frac(int t_frac, int r_frac_addr){
  //this function assumes you precharge beforehand
  Program p;
  p.add_inst(all_nops());
  int R_FRAC_REG = RF_REG;
  int bank_reg = BAR;
  p.add_inst(SMC_LI(r_frac_addr, R_FRAC_REG));

    /*       --Bank -> bank_reg--
    *        |  X  -------------- |-> rfrac_reg (R_FRAC_REG)
    *        | ... -------------- |
    *        | ... -------------- |
    *
    * Cmd:        ----| ACT R_FRAC_REG |------|       PRE      |------FINISH
    * Time:     T0----|       T1       |------|       T2       |------FINISH
    * Interval: -----------------------|t_frac|----------------|------FINISH
    */

  int num_cmd = 2 + t_frac;
  num_cmd += 4 - (num_cmd % 4);
  Mininst q_inst[num_cmd];
  for (int i = 0; i < num_cmd; i++)
    q_inst[i] = SMC_NOP();
  
  q_inst[0]          = SMC_ACT(bank_reg, 0, R_FRAC_REG, 0);
  q_inst[t_frac + 1] = SMC_PRE(bank_reg, 0, 0);

  for (int i = 0; i < num_cmd; i += 4)
    p.add_inst(q_inst[i], q_inst[i + 1], q_inst[i + 2], q_inst[i + 3]);

  return p;
  
}

Program _init(uint32_t bank_id,uint32_t num_iter)
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
Program test_prog(uint32_t num_iter, uint32_t bank_id, uint32_t n_open_rows, std::vector<uint32_t> &patterns, std::vector<uint32_t> &open_row_idx, \
                  uint32_t r_first, uint32_t r_second, std::vector<uint32_t> &r_frac_idx, 
                  uint32_t t_12, uint32_t t_23, uint32_t n_frac_times, uint32_t t_frac)
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
    for (int i = 0; i < r_frac_idx.size(); i++)
    {
      for(int j = 0; j < n_frac_times; j++)
      {
        program.add_inst(SMC_SLEEP(6));
        program.add_below(frac(t_frac,open_row_idx[r_frac_idx[i]]));
        program.add_inst(SMC_SLEEP(6));
      }
    }
    program.add_inst(SMC_SLEEP(6));
    program.add_below(PRE(BAR, 0, 0));
    program.add_inst(SMC_SLEEP(6));
    program.add_below(doubleACT(t_12, t_23, r_first, r_second));
    program.add_inst(SMC_SLEEP(6));
    program.add_below(PRE(BAR, 0, 0));
    program.add_inst(SMC_SLEEP(6));

    program.add_below(rdRow_immediate(BAR, open_row_idx[0]));
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

std::vector<uint8_t> maj_operation(std::vector<uint32_t> patterns, std::vector<uint32_t> r_frac_idx)
{
  //size of patterns
  int n_patterns = patterns.size();
  //majority operation
  std::vector <uint8_t> bit_maj;
  for(int j = 0; j < 32 ; j++)
  { 
    uint8_t temp = 0;
    for(int i = 0; i < n_patterns; i++)
    {
    //get majority of each bit
      temp += (patterns[i] >> j) & 0x1; 
    }
    for (int i = 0; i < r_frac_idx.size(); i++)
    {
      temp -= (patterns[r_frac_idx[i]] >> j) & 0x1;
    }
    int inp_size = n_patterns - r_frac_idx.size();
    bit_maj.push_back(temp > inp_size/2 ? 1 : 0);
  }
  return bit_maj;
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
int read_args_n_parse(int argc, char* argv[], std::vector<uint32_t> &r_frac_idx,
              uint32_t *r_first, uint32_t *r_second, 
              uint32_t *min_row, uint32_t *max_row, uint32_t *n_open_rows,
              std::vector<uint32_t> &patterns, std::vector<uint32_t> &open_row_idx,
              uint32_t *num_iter, uint32_t *bank_id, uint32_t *maj_x, 
              uint32_t *t_12, uint32_t *t_23, uint32_t *n_frac_times, uint32_t *t_frac,
              std::ofstream &out_file)
{

  if(argc != 17)
  {
    printf("Usage: \n ./quac-test <inp_pattern_file> <r_frac_idx_file> <r_first> <r_second> <min_row_idx> <max_row_idx> <n_open_rows> <inp_row_file> <num_iter> <bank_id> <maj_x> <t_12> <t_23> <n_frac_times> <t_frac> <out_file>\n");
    return(0); 
  }
  int arg_i = 1;
  parse_file(std::string(argv[arg_i++]), patterns);
  parse_file(std::string(argv[arg_i++]), r_frac_idx);
  *r_first     = atoi(argv[arg_i++]);
  *r_second    = atoi(argv[arg_i++]);
  *min_row =      atoi(argv[arg_i++]);
  *max_row =      atoi(argv[arg_i++]);
  *n_open_rows =  atoi(argv[arg_i++]);


  parse_file(std::string(argv[arg_i++]), open_row_idx);
  *num_iter     =  atoi(argv[arg_i++]);
  *bank_id      =  atoi(argv[arg_i++]);
  *maj_x        =  atoi(argv[arg_i++]);
  *t_12         =  atoi(argv[arg_i++]);
  *t_23         =  atoi(argv[arg_i++]);
  *n_frac_times =  atoi(argv[arg_i++]);
  *t_frac       =  atoi(argv[arg_i++]);
  

  out_file.open(std::string(argv[arg_i++]), std::ios::app);

  return 1;
}
void report_coverage_results(SoftMCPlatform &platform, std::vector<uint32_t> pattern, std::vector<uint32_t> r_frac_idx, uint32_t bank_id, uint32_t num_iter, uint32_t *maj_result, vector<uint32_t>& open_row_idx, bool is_stability)
{
  std::vector <uint8_t> expected_maj = maj_operation(pattern, r_frac_idx);
  uint8_t row[8192];
  
  platform.receiveData((void*)row, 8192);
  if(is_stability && DEBUG){
    std::cout << "Running test: " << std::endl;
    for(int i = 0; i < pattern.size(); i++)
    {
      if(std::find(r_frac_idx.begin(), r_frac_idx.end(), i) != r_frac_idx.end()){
        std::cout << std::setw(15) << open_row_idx[i] << ": ffffffffffffffffffffffffffffffff" << std::endl;
      }else{
        std::cout << std::setw(15) << open_row_idx[i] << ": " << std::bitset<32>(pattern[i]) << std::endl;
      }
    }
  }

  uint32_t exp_maj_result = 0;
  for(int i = 0; i < expected_maj.size(); i++)
  {
    exp_maj_result |= ((expected_maj[i] & 0x1) << i);
  }

  for(int j = 0; j < 8192/4; j++)
  {
    uint32_t read_maj_result = row[j*4] | (row[j*4+1] << 8) | (row[j*4+2] << 16) | (row[j*4+3] << 24);
    bitset<32> result(~(read_maj_result ^ exp_maj_result));
    for (int i = 0; i < 32; i++)
    {
      maj_result[j*32 + i] += result.test(i) ? 1 : 0;
    }
    
    if(is_stability && DEBUG){
      std::cout << std::endl;
      std::cout << "exp_maj_result:  " << std::bitset<32>(exp_maj_result) << std::endl;
      std::cout << "read_maj_result: " << std::bitset<32>(read_maj_result) << std::endl;
      std::cout << "correct_res_ctr: ";
      for(int i = 31; i >= 0; i--)
      {
        std::cout << maj_result[j*32 + i];
      }
      std::cout << std::endl;
      break;
    }
  }

}
std::vector<uint32_t> random_pattern_creator(std::vector<uint32_t> r_frac_idx, uint32_t n_open_rows, uint32_t maj_x,uint32_t seed)
{
  std::vector<uint32_t> pattern_maj;
  std::vector<uint32_t> patterns;
  parse_file("./patterns/pattern_0.txt", patterns);
  srand((time(NULL)+getpid()+seed));
  for(int i = 0; i < maj_x; i++)
  {
    uint32_t wr_pattern = (uint32_t)rand();
    wr_pattern = (wr_pattern & 0xffff) | (uint32_t)rand() << 16;
    pattern_maj.push_back(wr_pattern);
  }
  for(int i = 0; i < n_open_rows; i++)
  {
    patterns[i]=(pattern_maj[i%maj_x]);
  }
  for(int i = 0; i < r_frac_idx.size(); i++)
  {
    patterns[r_frac_idx[i]] = ONE;
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



  if(!read_args_n_parse(argc, argv, r_frac_idx,
                &r_first, &r_second, 
                &min_row, &max_row, &n_open_rows,
                patterns_old, open_row_idx, 
                &num_iter, &bank_id, &maj_x,
                &t_12, &t_23, &n_frac_times, &t_frac,
               out_file))
  {
    exit(0);
  }

  if ((err = platform.init()) != SOFTMC_SUCCESS)
  {
    cerr << "Could not initialize SoftMC Platform: " << err << endl;
  }
  platform.reset_fpga();

  if(DEBUG){
    std::cout << "------------DEBUG------------" << std::endl;
    std::cout << "num_open_rows: " << n_open_rows << std::endl;
    std::cout << "maj_x: " << maj_x << std::endl;
    std::cout << "frac idx: " << std::endl;
    for(auto frac_idx : r_frac_idx)
    {
      std::cout << frac_idx << ", ";
    }
    std::cout << std::endl;
    std::cout << "open row idx: " << std::endl;
    for(auto open_row : open_row_idx)
    {
      std::cout << open_row << ", ";
    }
    std::cout << std::endl;
    std::cout << "r_first: " << r_first << std::endl;
    std::cout << "r_second: " << r_second << std::endl;
    std::cout << "-----------------------------" << std::endl;
  }



  uint32_t coverage_result[8192*8] {0};
  std::vector<std::string> pattern_files;

  uint32_t num_patterns = 0;
  for (boost::filesystem::directory_entry& entry : boost::filesystem::directory_iterator("./patterns/"))
  {
    num_patterns++;
    std::vector<uint32_t> patterns;
    parse_file(entry.path().string(), patterns);
    Program program = test_prog(num_iter,bank_id, n_open_rows, patterns, open_row_idx, r_first, r_second, r_frac_idx, t_12, t_23, n_frac_times, t_frac);
    platform.execute(program);
    report_coverage_results(platform, patterns, r_frac_idx, bank_id, num_iter, coverage_result, open_row_idx, false);
  }
  int stability_iter_count = 1000;
  uint32_t stability_result[8192*8] {0};
  for(int ii = 0; ii < stability_iter_count; ii++)
  {
    std::vector<uint32_t> random_patterns = random_pattern_creator(r_frac_idx,n_open_rows,maj_x,ii);

    Program program = test_prog(num_iter,bank_id, n_open_rows, random_patterns, open_row_idx, r_first, r_second, r_frac_idx, t_12, t_23, n_frac_times, t_frac);
    platform.execute(program);
    report_coverage_results(platform, random_patterns, r_frac_idx, bank_id, num_iter, stability_result, open_row_idx, true);
  }
  double avg_stability = 0.0;
  double avg_coverage = 0.0;
  double max_stability = 0.0;
  double min_stability = 0.0;
  uint32_t num_full_coverage_cells = 0;
  uint32_t num_full_stable_cells = 0;
  for(int j = 0; j < 8192*8; j++)
  {
    if(coverage_result[j] == num_patterns)
    {
      num_full_coverage_cells++;

    }
    avg_coverage += (double)coverage_result[j]/(double)num_patterns;
    if(stability_result[j] == stability_iter_count)
    {
      num_full_stable_cells++;
    }
    double stability = (double)stability_result[j]/(double)stability_iter_count;
    avg_stability += stability;
  }
  out_file << std::to_string((avg_coverage/65536.0)*100.0) << ",";
  out_file << std::to_string(((double)num_full_coverage_cells/65536.0)*100.0) << ",";
  out_file << std::to_string((avg_stability/65536.0)*100.0) << ",";
  out_file << std::to_string(((double)num_full_stable_cells/65536.0)*100.0);
  out_file.close();
  
  return 0;
}