//
// FILE: treedrag.h -- Interface to dragging implementation classes
//
//
//

#ifndef TREEDRAG_H
#define TREEDRAG_H

typedef enum { DRAG_NODE_START = 0, DRAG_NODE_END = 1,
	       DRAG_ISET_START = 2, DRAG_ISET_END = 3,
	       DRAG_BRANCH_START = 4, DRAG_BRANCH_END = 5,
	       DRAG_OUTCOME_START = 6, DRAG_OUTCOME_END = 7 } guiDragType;

typedef enum { DRAG_NONE = 0, DRAG_START = 1, DRAG_CONTINUE = 2,
	       DRAG_STOP = 3 } guiDragState;

//
// This class enables the user to grab a node and drag it to a terminal node.
// When the mouse is released, a copy or move (if Control is down) action is
// performed.
//
class TreeWindow::NodeDragger {
private:
  Efg &ef;
  wxBitmap *m_b, *c_b;
  wxMemoryDC *move_dc, *copy_dc;
  TreeWindow *parent;
  wxCanvasDC *dc;
  int drag_now;
  float x, y, ox, oy;  // position and old position
  int c, oc; // control pressed and old control pressed
  Node *start_node, *end_node;
    
  void RedrawObject(void);
    
public:
  NodeDragger(TreeWindow *parent, Efg &ef);
  ~NodeDragger();
    
  int OnEvent(wxMouseEvent &ev, Bool &nodes_changed);

  int ControlDown(void) const { return c; }
  int Dragging(void) const { return drag_now; }
    
  Node *StartNode(void) { return start_node; }
  Node *EndNode(void) { return end_node; }
};


//
// This class enables the user to merge infosets by dragging a line from the
// first infoset's maker to the second one's.
//
class TreeWindow::IsetDragger {
private:
  Efg &ef;
  TreeWindow *parent;
  wxCanvasDC *dc;
  int drag_now;
  float x, y, ox, oy, sx, sy;    // current, previous, start positions
  Node *start_node, *end_node;
    
  void RedrawObject(void);
    
public:
  IsetDragger(TreeWindow *parent, Efg &ef);
  ~IsetDragger();
    
  int OnEvent(wxMouseEvent &ev, Bool &infosets_changed);
  int Dragging(void) const { return drag_now; }
    
  Node *StartNode(void) { return start_node; }
  Node *EndNode(void) { return end_node; }
};

//
// This class allows the user to add branches to a node/infoset by dragging a
// line from the base of the branches to the position the new branch is to
// occupy.  If the node was terminal, a player dialog is opened to 
// choose a player.
//
class TreeWindow::BranchDragger {
private:
  Efg &ef;
  TreeWindow *parent;
  wxCanvasDC *dc;
  int drag_now;
  int br;
  float x, y, ox, oy, sx, sy;    // current, previous, start positions
  Node *start_node;
    
  void RedrawObject(void);
    
public:
  BranchDragger(TreeWindow *parent, Efg &ef);
  ~BranchDragger();
    
  int OnEvent(wxMouseEvent &ev, Bool &infosets_changed);
  int Dragging(void) const { return drag_now; }
    
  Node *StartNode(void) { return start_node; }
  int BranchNum(void) { return br; }
};


class TreeWindow::OutcomeDragger {
private:
  Efg &ef;
  TreeWindow *parent;
  int drag_now;
  EFOutcome *outcome;
  Node *start_node;
  float x, y;
  wxCursor *outcome_cursor;
    
public:
  OutcomeDragger(TreeWindow *parent, Efg &ef);
  ~OutcomeDragger();
    
  int Dragging(void) const { return drag_now; }
  int OnEvent(wxMouseEvent &ev, Bool &outcomes_changed);
};


#endif  // TREEDRAG_H

