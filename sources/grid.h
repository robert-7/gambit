//#
//# FILE: grid.h -- Interface to grid-solve module
//#
//# $Id$
//#

#ifndef GRID_H
#define GRID_H

#ifdef __GNUG__
#pragma interface
#endif   // __GNUG__

#include "g2dblock.h"

template <class T> class GridParams   {
  public:
    T minLam, maxLam, delLam, delp, tol;
    int type, plev;
    gOutput *outfile, *errfile, *pxifile;
    void  (*update_func)(double);

    GridParams(void);
    GridParams(const GridParams<T> &p);
    int Ok(void) const;	// check the validity of the paramters
};

template <class T> class PayoffClass   {
  public:
    T row, col;
};

template <class T> class GridSolveModule  {
  private:
    const NormalForm<T> &nf;
    gVector<T> p, x, q_calc, y;
    const GridParams<T> &params;
    g2DBlock<PayoffClass<T> > matrix;

    int CheckEqu(gVector<T> &q,T l);
    void OutputResult(T l,T dist,gVector<T> &q,gVector<T> &p);
    void OutputHeader(void);

  public:
    GridSolveModule(const NormalForm<T> &r,const GridParams<T> &param);
    //	GridSolveModule(const NormalForm<T> &r,gInput &param);
    ~GridSolveModule();
    int GridSolve(void);
};

#endif    // GRID_H

