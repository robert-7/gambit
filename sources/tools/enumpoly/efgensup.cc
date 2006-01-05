//
// $Source$
// $Date$
// $Revision$
//
// DESCRIPTION:
// Enumerate undominated subsupports
//
// This file is part of Gambit
// Copyright (c) 2002, The Gambit Project
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
//

#include "efgensup.h"

// We build a series of functions of increasing complexity.  The
// final one, which is our goal, is the undominated support function.
// We begin by simply enumerating all subsupports.

void AllSubsupportsRECURSIVE(const gbtEfgSupport &s,
			     gbtEfgSupportWithActiveInfo *sact,
			     ActionCursorForSupport *c,
			     gbtList<gbtEfgSupport> &list)
{ 
  list.Append(sact->UnderlyingSupport());

  ActionCursorForSupport c_copy(*c);

  do {
    if ( sact->ActionIsActive(c_copy.GetAction()) ) {
      sact->RemoveAction(c_copy.GetAction());
      AllSubsupportsRECURSIVE(s,sact,&c_copy,list);
      sact->AddAction(c_copy.GetAction());
    }
  } while (c_copy.GoToNext()) ;
}

gbtList<gbtEfgSupport> AllSubsupports(const gbtEfgSupport &S)
{
  gbtList<gbtEfgSupport> answer;
  gbtEfgSupportWithActiveInfo SAct(S);
  ActionCursorForSupport cursor(S);

  AllSubsupportsRECURSIVE(S, &SAct, &cursor, answer);

  return answer;
}


// Subsupports of a given support are _path equivalent_ if they
// agree on every infoset that can be reached under either, hence both,
// of them.  The next routine outputs one support for each equivalence
// class.  It is not for use in solution routines, but is instead a 
// prototype of the eventual path enumerator, which will also perform
// dominance elimination.

void AllInequivalentSubsupportsRECURSIVE(const gbtEfgSupport &s,
					 gbtEfgSupportWithActiveInfo *sact,
					 ActionCursorForSupport *c,
					 gbtList<gbtEfgSupport> &list)
{ 
  if (sact->HasActiveActionsAtActiveInfosetsAndNoOthers())
    list.Append(sact->UnderlyingSupport());

  ActionCursorForSupport c_copy(*c);

  do {
    if ( sact->ActionIsActive(c_copy.GetAction()) ) {

      gbtList<Gambit::GameInfoset> deactivated_infosets;
      sact->RemoveActionReturningDeletedInfosets(c_copy.GetAction(),
						 &deactivated_infosets); 

      if (!c_copy.DeletionsViolateActiveCommitments(sact,
						    &deactivated_infosets))
	AllInequivalentSubsupportsRECURSIVE(s,sact,&c_copy,list);
      sact->AddAction(c_copy.GetAction());
    }
  } while (c_copy.GoToNext()) ;
}

gbtList<gbtEfgSupport> AllInequivalentSubsupports(const gbtEfgSupport &S)
{
  gbtList<gbtEfgSupport> answer;
  gbtEfgSupportWithActiveInfo SAct(S);
  ActionCursorForSupport cursor(S);

  AllInequivalentSubsupportsRECURSIVE(S, &SAct, &cursor, answer);

  return answer;
}

void AllUndominatedSubsupportsRECURSIVE(const gbtEfgSupport &s,
					gbtEfgSupportWithActiveInfo *sact,
					ActionCursorForSupport *c,
					bool strong, bool conditional,
					gbtList<gbtEfgSupport> &list)
{ 
  bool abort = false;
  bool no_deletions = true;
  bool check_domination = false;
  if (sact->HasActiveActionsAtActiveInfosets()) 
    check_domination = true;
  gbtList<Gambit::GameAction> deletion_list;
  ActionCursorForSupport scanner(s);

  // First we collect all the actions that can be deleted.
  do {
    Gambit::GameAction this_action = scanner.GetAction();
    bool delete_this_action = false;

    if ( sact->ActionIsActive(this_action) ) 
      if ( !sact->InfosetIsActive(this_action->GetInfoset()) ) 
	delete_this_action = true;  
      else 
	if (check_domination) 
	  if (sact->IsDominated(this_action,strong,conditional) ) 
	    delete_this_action = true;
	
    if (delete_this_action) {
      no_deletions = false;
      if (c->IsSubsequentTo(this_action)) 
	abort = true;
      else 
	deletion_list.Append(this_action);
    }
  } while (!abort && scanner.GoToNext());

  // Now we delete them, recurse, then restore
  if (!abort && !no_deletions) {
    gbtList<Gambit::GameAction> actual_deletions;
    for (int i = 1; !abort && i <= deletion_list.Length(); i++) {
      actual_deletions.Append(deletion_list[i]);
      gbtList<Gambit::GameInfoset> deactivated_infosets;
      
      sact->RemoveActionReturningDeletedInfosets(deletion_list[i],
						   &deactivated_infosets); 
	
      if (c->DeletionsViolateActiveCommitments(sact,&deactivated_infosets))
	abort = true;
    }

    if (!abort)
      AllUndominatedSubsupportsRECURSIVE(s,
					 sact,
					 c,
					 strong,
					 conditional,
					 list);
    
    for (int i = 1; i <= actual_deletions.Length(); i++)
      sact->AddAction(actual_deletions[i]);
  }

  // If there are no deletions, we ask if it is consistent, then recurse.
  if (!abort && no_deletions) {
    if (sact->HasActiveActionsAtActiveInfosetsAndNoOthers())
      list.Append(sact->UnderlyingSupport());
    
    ActionCursorForSupport c_copy(*c);
    
    do {
      if ( sact->ActionIsActive(c_copy.GetAction()) ) {
	
	gbtList<Gambit::GameInfoset> deactivated_infosets;
	sact->RemoveActionReturningDeletedInfosets(c_copy.GetAction(),
						   &deactivated_infosets); 
	
	if (!c_copy.DeletionsViolateActiveCommitments(sact,
						      &deactivated_infosets))
	  AllUndominatedSubsupportsRECURSIVE(s,
					     sact,
					     &c_copy,
					     strong,
					     conditional,
					     list);
	sact->AddAction(c_copy.GetAction());
	
      }
    } while (c_copy.GoToNext()) ;
  }
}
  
gbtList<gbtEfgSupport> AllUndominatedSubsupports(const gbtEfgSupport &S,
					       bool strong, bool conditional)
{
  gbtList<gbtEfgSupport> answer;
  gbtEfgSupportWithActiveInfo sact(S);
  ActionCursorForSupport cursor(S);

  AllUndominatedSubsupportsRECURSIVE(S,
				     &sact,
				     &cursor,
				     strong,
				     conditional,
				     answer);

  return answer;
}

void PossibleNashSubsupportsRECURSIVE(const gbtEfgSupport &s,
				      gbtEfgSupportWithActiveInfo *sact,
				      ActionCursorForSupport *c,
				      gbtList<gbtEfgSupport> &list)
{ 
  bool abort = false;
  bool add_support = true;

  bool check_domination = false;
  if (sact->HasActiveActionsAtActiveInfosets()) 
    check_domination = true;
  gbtList<Gambit::GameAction> deletion_list;
  ActionCursorForSupport scanner(s);

  do {
    Gambit::GameAction this_action = scanner.GetAction();
    bool delete_this_action = false;

    if ( sact->ActionIsActive(this_action) ) 
      if ( !sact->InfosetIsActive(this_action->GetInfoset()) )
	delete_this_action = true;  
      else
	if (check_domination) 
	  if ( sact->IsDominated(this_action,true,true) ||
	       sact->IsDominated(this_action,true,false) ) {
	    add_support = false;
	    if ( c->InfosetGuaranteedActiveByPriorCommitments(sact,
						   this_action->GetInfoset()) )
	      delete_this_action = true;
	  }
    if (delete_this_action) {
      if (c->IsSubsequentTo(this_action)) 
	abort = true;
      else 
	deletion_list.Append(this_action);
    }
  } while (!abort && scanner.GoToNext());
  
  if (!abort) {
    gbtList<Gambit::GameAction> actual_deletions;
    for (int i = 1; !abort && i <= deletion_list.Length(); i++) {
      actual_deletions.Append(deletion_list[i]);
      gbtList<Gambit::GameInfoset> deactivated_infosets;
      sact->RemoveActionReturningDeletedInfosets(deletion_list[i],
						   &deactivated_infosets); 
      if (c->DeletionsViolateActiveCommitments(sact,&deactivated_infosets))
	abort = true;
    }

    if (!abort && deletion_list.Length() > 0) 
      PossibleNashSubsupportsRECURSIVE(s,sact,c,list);
        
    for (int i = 1; i <= actual_deletions.Length(); i++) {
      sact->AddAction(actual_deletions[i]);
    }
  }

  if (!abort && deletion_list.Length() == 0) {

    if (add_support && sact->HasActiveActionsAtActiveInfosetsAndNoOthers())
      list.Append(sact->UnderlyingSupport());    
    ActionCursorForSupport c_copy(*c);
    do {
      if ( sact->ActionIsActive(c_copy.GetAction()) ) {
	gbtList<Gambit::GameInfoset> deactivated_infosets;
	sact->RemoveActionReturningDeletedInfosets(c_copy.GetAction(),
						   &deactivated_infosets); 
	if (!c_copy.DeletionsViolateActiveCommitments(sact,
						      &deactivated_infosets))
	  PossibleNashSubsupportsRECURSIVE(s,sact,&c_copy,list);

	sact->AddAction(c_copy.GetAction());
      }
    } while (c_copy.GoToNext()) ;
  }
}

gbtList<gbtEfgSupport> SortSupportsBySize(gbtList<gbtEfgSupport> &list) 
{
  gbtArray<int> sizes(list.Length());
  for (int i = 1; i <= list.Length(); i++)
    sizes[i] = list[i].NumDegreesOfFreedom();

  gbtArray<int> listproxy(list.Length());
  for (int i = 1; i <= list.Length(); i++)
    listproxy[i] = i;

  int maxsize(0);
  for (int i = 1; i <= list.Length(); i++)
    if (sizes[i] > maxsize)
      maxsize = sizes[i];

  int cursor(1);

  for (int j = 0; j < maxsize; j++) {
    int scanner(list.Length());
    while (cursor < scanner)
      if (sizes[scanner] != j)
	scanner--;
      else {
	while (sizes[cursor] == j)
	  cursor++;
	if (cursor < scanner) {
	  int tempindex = listproxy[cursor];
	  listproxy[cursor] = listproxy[scanner];
	  listproxy[scanner] = tempindex;
	  int tempsize = sizes[cursor];
	  sizes[cursor] = sizes[scanner];
	  sizes[scanner] = tempsize;
	  cursor++;
	}
      }
  }

  gbtList<gbtEfgSupport> answer;
  for (int i = 1; i <= list.Length(); i++)
    answer.Append(list[listproxy[i]]);

  return answer;
}
  
gbtList<gbtEfgSupport> PossibleNashSubsupports(const gbtEfgSupport &S)
{
  gbtList<gbtEfgSupport> answer;
  gbtEfgSupportWithActiveInfo sact(S);
  ActionCursorForSupport cursor(S);

  PossibleNashSubsupportsRECURSIVE(S, &sact, &cursor, answer);

  // At this point answer has all consistent subsupports without
  // any strong dominations.  We now edit the list, removing all
  // subsupports that exhibit weak dominations, and we also eliminate
  // subsupports exhibiting domination by currently inactive actions.

  for (int i = answer.Length(); i >= 1; i--) {
    gbtEfgSupportWithActiveInfo current(answer[i]);
    ActionCursorForSupport crsr(S);
    bool remove = false;
    do {
      Gambit::GameAction act = crsr.GetAction();
      if (current.ActionIsActive(act)) 
	for (int j = 1; j <= act->GetInfoset()->NumActions(); j++) {
	  Gambit::GameAction other_act = act->GetInfoset()->GetAction(j);
	  if (other_act != act)
	    if (current.ActionIsActive(other_act)) {
	      if (current.Dominates(other_act,act,false,true) ||
		  current.Dominates(other_act,act,false,false)) 
		remove = true;
	    }
	    else { 
	      current.AddAction(other_act);
	      if (current.HasActiveActionsAtActiveInfosetsAndNoOthers())
		if (current.Dominates(other_act,act,false,true) ||
		    current.Dominates(other_act,act,false,false)) {
		  remove = true;
		}
	      current.RemoveAction(other_act);
	    }
      }
    } while (crsr.GoToNext() && !remove);
    if (remove)
      answer.Remove(i);
  }

  return SortSupportsBySize(answer);
}

//----------------------------------------------------
//                ActionCursorForSupport
// ---------------------------------------------------

ActionCursorForSupport::ActionCursorForSupport(const gbtEfgSupport &S)
  : support(&S), pl(1), iset(1), act(1)
{
  Gambit::Game efg = S.GetGame();

  // Make sure that (pl,iset) points to a valid information set:
  // when solving by subgames, some players may not have any information
  // sets at all.
  for (pl = 1; pl <= efg->NumPlayers(); pl++) {
    if (efg->GetPlayer(pl)->NumInfosets() > 0) {
      for (iset = 1; iset <= efg->GetPlayer(pl)->NumInfosets(); iset++) {
	if (S.NumActions(pl, iset) > 0) {
	  return;
	}
      }
    }
  }
}

ActionCursorForSupport::ActionCursorForSupport(
                  const ActionCursorForSupport &ac)
  : support(ac.support), pl(ac.pl), iset(ac.iset), act(ac.act)
{}

ActionCursorForSupport::~ActionCursorForSupport()
{}

ActionCursorForSupport& 
ActionCursorForSupport::operator=(const ActionCursorForSupport &rhs)
{
  if (this != &rhs) {
    support = rhs.support;
    pl = rhs.pl;
    iset = rhs.iset;
    act = rhs.act;
  }
  return *this;
}

bool 
ActionCursorForSupport::operator==(const ActionCursorForSupport &rhs) const
{
  if (support != rhs.support ||
      pl      != rhs.pl      ||
      iset    != rhs.iset    ||
      act != rhs.act)
    return false;
  return true;
}

bool 
ActionCursorForSupport::operator!=(const ActionCursorForSupport &rhs) const
{
 return (!(*this==rhs));
}

bool
ActionCursorForSupport::GoToNext()
{
  if (act != support->NumActions(pl,iset))
    { act++; return true; }
  
  int temppl(pl);
  int tempiset(iset);
  tempiset ++; 

  while (temppl <= support->GetGame()->NumPlayers()) {
    while (tempiset <= support->GetGame()->GetPlayer(temppl)->NumInfosets()) {
      if (support->NumActions(temppl,tempiset) > 0) {
	pl = temppl;
	iset = tempiset;
	act = 1;
	return true;
      }
      else
	tempiset++;
    }
    tempiset = 1;
    temppl++;
  }
  return false;
}

Gambit::GameAction ActionCursorForSupport::GetAction() const
{
  return support->Actions(pl,iset)[act];
}

int ActionCursorForSupport::ActionIndex() const
{
  return act;
}


Gambit::GameInfoset ActionCursorForSupport::GetInfoset() const
{
  return support->GetGame()->GetPlayer(pl)->GetInfoset(iset);
}

int ActionCursorForSupport::InfosetIndex() const
{
  return iset;
}

Gambit::GamePlayer ActionCursorForSupport::GetPlayer() const
{
  return support->GetGame()->GetPlayer(pl);
}

int ActionCursorForSupport::PlayerIndex() const
{
  return pl;
}

bool 
ActionCursorForSupport::IsLast() const
{
  if (pl == support->GetGame()->NumPlayers())
    if (iset == support->GetGame()->GetPlayer(pl)->NumInfosets())
      if (act == support->NumActions(pl,iset))
	return true;
  return false;
}

bool 
ActionCursorForSupport::IsSubsequentTo(const Gambit::GameAction &a) const
{
  if (pl > a->GetInfoset()->GetPlayer()->GetNumber())
    return true; 
  else if (pl < a->GetInfoset()->GetPlayer()->GetNumber())
    return false;
  else
    if (iset > a->GetInfoset()->GetNumber())
      return true; 
    else if (iset < a->GetInfoset()->GetNumber())
      return false;
    else 
      if (act > a->GetNumber())
	return true;
      else
	return false;
}


bool ActionCursorForSupport::
DeletionsViolateActiveCommitments(const gbtEfgSupportWithActiveInfo *S,
				   const gbtList<Gambit::GameInfoset> *infosetlist)
{
  for (int i = 1; i <= infosetlist->Length(); i++) {
    Gambit::GameInfoset infoset = (*infosetlist)[i];
    if (infoset->GetPlayer()->GetNumber() < PlayerIndex() ||
	( infoset->GetPlayer()->GetNumber() == PlayerIndex() &&
	  infoset->GetNumber() < InfosetIndex()) )
      if (S->NumActions(infoset) > 0)
	return true;
    if (infoset->GetPlayer()->GetNumber() == PlayerIndex() &&
	infoset->GetNumber() == InfosetIndex() )
      for (int act = 1; act < ActionIndex(); act++)
	if ( S->ActionIsActive(infoset->GetPlayer()->GetNumber(),
			       infoset->GetNumber(),
			       act) )
	  return true;
  }
  return false;
}


bool ActionCursorForSupport::
InfosetGuaranteedActiveByPriorCommitments(const gbtEfgSupportWithActiveInfo *S,
					  const Gambit::GameInfoset &infoset)
{
  gbtList<Gambit::GameNode> members;
  for (int i = 1; i <= infoset->NumMembers(); i++) {
    members.Append(infoset->GetMember(i));
  }

  for (int i = 1; i <= members.Length(); i++) {
    Gambit::GameNode current = members[i];
    if ( current == S->GetGame()->GetRoot() )
      return true;
    else
      while ( S->ActionIsActive(current->GetPriorAction()) &&
	      IsSubsequentTo(current->GetPriorAction()) ) {
	current = current->GetParent();
	if ( current == S->GetGame()->GetRoot() )
	  return true;
      }
  }
  return false;
}
