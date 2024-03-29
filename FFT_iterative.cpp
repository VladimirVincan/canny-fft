#include <iostream>
#include <stdio.h>
#include <math.h>
#include "matrix_operators.hpp"

using namespace std;
double wCOS[128000];
double wSIN[128000];

void initTwiddle(int size)
{
  for (int k = 0; k < size; ++k){
    wCOS[k] = cos(-2.0*PI*k / size);
    wSIN[k] = sin(-2.0*PI*k / size);
  }
}

void butterfly(
  double topRE_i,
  double topIM_i,
  double bottomRE_i,
  double bottomIM_i,
  double *topRE_o,
  double *topIM_o,
  double *bottomRE_o,
  double *bottomIM_o,
  int k)
{
  double botRE = bottomRE_i * wCOS[k] - bottomIM_i * wSIN[k];
  double botIM = bottomRE_i * wSIN[k] + bottomIM_i * wCOS[k];

  // if(bottomRE_i == 1)
  //   {cout << "wCOS[" << k << "] = " << wCOS[k] << endl;
  // cout << "wSIN[" << k << "] = " << wSIN[k] << endl;
    // }
  *topRE_o = topRE_i + botRE;
  *topIM_o = topIM_i + botIM;
  *bottomRE_o = topRE_i - botRE;
  *bottomIM_o = topIM_i - botIM;
}

void FFT_complex_iterative(
  int size,
  int log2size,
  double *dataRE,
  double *dataIM
)
{
  // cout << "START" << endl;
  // for (int i = 0; i<size; ++i)
  //   cout << dataRE[i] << " ";
  // cout << endl;
  // cout << "log2size = " << log2size << endl;

  for (int i=0; i < log2size-1; ++i){
    int m = 1 << (i+1);
    int m2 = 1 << i; // "half of m"
    for (int j=0; j < m2; ++j){
      for (int k=j; k < size; k+=m){
        double topRE = dataRE[k];
        double topIM = dataIM[k];
        double bottomRE = dataRE[k+m2];
        double bottomIM = dataIM[k+m2];
        butterfly(
          topRE,
          topIM,
          bottomRE,
          bottomIM,
          dataRE+k,
          dataIM+k,
          dataRE+k+m2,
          dataIM+k+m2,
          j << (log2size-i-2) );
      }
    }
    // for (int l = 0; l<size; ++l)
    //   cout << dataRE[l] << " ";
    // cout << endl;
  }
  // cout << "FINAL" << endl;
  // for (int l = 0; l<size; ++l)
  //   cout << dataRE[l] << " ";
  // cout << endl << endl;
}

void FFT2D_complex_iterative(
  int height, int log2h,
  int width, int log2w,
  double **matrixDataRE,
  double **matrixDataIM)
{
  // allocate memory - height and width are both of 2^n type

  int max_size;
  if (height > width)
    max_size = height;
  else
    max_size = width;

  double *dataRE = new double [max_size];
  double *dataIM = new double [max_size];
  for (int i=0;i<max_size;++i)
    dataRE[i]=dataIM[i]=0;

  // bit reverasal & horizontal FFT

  for (int i = 0; i< height; ++i){
    for (int j = 0; j < width; ++j){
      int reversed = 0;
      int temp = j;
      for (int k = 0; k < log2w-1; ++k){
        reversed = reversed << 1;
        reversed = reversed | (temp&1);
        temp = temp >> 1;
      }
      dataRE[j] = matrixDataRE[i][reversed];
      dataIM[j] = matrixDataIM[i][reversed];

    }

    // for (int k=0;k<width;++k)
    //   cout << dataRE[k] << " ";
    // cout << endl;
    FFT_complex_iterative(width, log2w, dataRE, dataIM);
    // for (int k=0;k<width;++k)
    //   cout << dataRE[k] << " ";
    // cout << endl;

    for (int j=0; j < width; ++j){
      matrixDataRE[i][j] = dataRE[j];
      matrixDataIM[i][j] = dataIM[j];
    }
  }

  // cout << "matrixDataRE= " << endl;
  // print_matrix(height,width,matrixDataRE);
  // cout << endl;

  // cout << "matrixDataIM= " << endl;
  // print_matrix(height,width,matrixDataIM);
  // cout << endl;

  // bit reversal & vertical FFT

  for (int j =0;j<width; ++j){
    for (int i=0;i<height; ++i){
      int reversed = 0;
      int temp = i;
      for (int k = 0; k < log2h-1; ++k){
        reversed = reversed << 1;
        reversed = reversed | (temp&1);
        temp = temp >> 1;
      }
      dataRE[i] = matrixDataRE[reversed][j],
      dataIM[i] = matrixDataIM[reversed][j];
    }
    FFT_complex_iterative(height, log2h, dataRE, dataIM);

    for (int i=0;i<height; ++i){
      matrixDataRE[i][j] = dataRE[i];
      matrixDataIM[i][j] = dataIM[i];
    }
  }
  delete dataRE;
  delete dataIM;
}

void matrix_convolution(
  int height, int width,
  int log2h, int log2w,
  double **a,
  double **b,
  double **c)
{
  // allocate memory

  initTwiddle(max(height,width));

  double **aRE;
  alloc_matrix(height, width, &aRE);
  for (int i=0;i<height;++i)
    for (int j=0;j<width;++j)
      aRE[i][j] = a[i][j];

  double **bRE;
  alloc_matrix(height, width, &bRE);
  for (int i=0;i<height;++i)
    for (int j=0;j<width;++j)
      bRE[i][j] = b[i][j];

  double **aIM;
  alloc_matrix(height, width, &aIM);

  double **bIM;
  alloc_matrix(height, width, &bIM);

  double **cRE;
  alloc_matrix(height, width, &cRE);

  double **cIM;
  alloc_matrix(height, width, &cIM);

  // calculate

  // cout << "before fft2 A" << endl;
  FFT2D_complex_iterative(
    height, log2h,
    width, log2w,
    aRE, aIM);

  // cout << "before fft2 B" << endl;
  // cout << endl << "| BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB |" << endl;
  // cout << endl << "| BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB |" << endl;
  // cout << endl << "| BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB |" << endl;
  // cout << endl << endl;

  FFT2D_complex_iterative(
    height, log2h,
    width, log2w,
    bRE, bIM);

  // cout << "aRE= " << endl;
  // print_matrix(height,width,aRE);
  // cout << endl;

  // cout << "aIM= " << endl;
  // print_matrix(height,width,aIM);
  // cout << endl;

  // cout << "bRE= " << endl;
  // print_matrix(height,width,bRE);
  // cout << endl;

  // cout << "bIM= " << endl;
  // print_matrix(height,width,bIM);
  // cout << endl;

  for (int i=0; i<height; ++i)
    for (int j=0; j<width; ++j){
      cRE[i][j] = aRE[i][j] * bRE[i][j] - aIM[i][j] * bIM[i][j];
      cIM[i][j] = - (aRE[i][j] * bIM[i][j] + aIM[i][j] * bRE[i][j]);
    }

  FFT2D_complex_iterative(
    height, log2h,
    width, log2w,
    cRE, cIM);

  for (int i=0;i<height;++i)
    for (int j=0;j<width;++j)
      c[i][j] = cRE[i][j]/(width*height);

  delete[] aRE;
  delete[] aIM;
  delete[] bRE;
  delete[] bIM;
  delete[] cRE;
  delete[] cIM;
}






namespace {
extern "C" {
#ifdef PYTHON3_MODULE
int main(){
  int n = 4;
  int height = 4, width = 4;

  double **a;
  alloc_matrix(height, width, &a);
  for (int i=0;i<height;++i)
    for (int j=0;j<width;++j)
      a[i][j] = 0;
  a[3][3] = 1;

  double **b;
  alloc_matrix(height, width, &b);
  for (int i=0;i<height;++i)
    for (int j=0;j<width;++j)
      b[i][j] = 0;
  b[3][0] = 1;
  b[3][1] = 1;
  b[3][2] = 1;
  b[3][3] = 1;

  double **c;
  alloc_matrix(height, width, &c);
  for (int i=0;i<height;++i)
    for (int j=0;j<width;++j)
      c[i][j] = 0;

  matrix_convolution(n,n,2,2,a,b,c);

  printf("a=\n");
  for (int i = 0; i < height; ++i){
    for (int j = 0; j < width; ++j)
      printf("%.2f ", a[i][j]);
    printf("\n");
  }
  printf("\nb=\n");
  for (int i = 0; i < height; ++i){
    for (int j = 0; j < width; ++j)
      printf("%.2f ", b[i][j]);
    printf("\n");
  }
  printf("\nc=\n");
  for (int i = 0; i < height; ++i){
    for (int j = 0; j < width; ++j)
      printf("%.2f ", c[i][j]);
    printf("\n");
  }

  return 0;
}
#endif // PYTHON3_MODULE
}
}
