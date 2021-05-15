from constants import *
from utils import *
from core import *

import pdb
import copy
from functools import reduce

from statesactions import *

############################
## HELPERS

### Return true if the given state object is a goal. Goal is a State object too.
def is_goal(state, goal):
  return len(goal.propositions.difference(state.propositions)) == 0

### Return true if the given state is in a set of states.
def state_in_set(state, set_of_states):
  for s in set_of_states:
    if s.propositions == state.propositions:
      return True
  return False

### For debugging, print each state in a list of states
def print_states(states):
  for s in states:
    ca = None
    if s.causing_action is not None:
      ca = s.causing_action.name
    print(s.id, s.propositions, ca, s.get_g(), s.get_h(), s.get_f())

## Takes a precondition, list of edges, and visitedset and returns true 
  ## if the precondition is in one of the edges and that edge's originating action
  ## is in visited set
def isPreconditionInEdgeAndOriginatedFromVS(precondition, edges, visitedSet):
  for edge in edges:
    if (edge[1] == precondition) & (edge[0] in visitedSet):
      return True
  return False

  ## Takes action and edges and visited sets
  ## returns True if the action is queable.
def isActionSatisfied(action, edges, visitedSet):
  for precondition in action.preconditions:
    if not isPreconditionInEdgeAndOriginatedFromVS(precondition, edges, visitedSet):
      return False
  return True
############################
### Planner 
###
### The planner knows how to generate a plan using a-star and heuristic search planning.
### It also knows how to execute plans in a continuous, time environment.

class Planner():

  def __init__(self):
    self.running = False              # is the planner running?
    self.world = None                 # pointer back to the world
    self.the_plan = []                # the plan (when generated)
    self.initial_state = None         # Initial state (State object)
    self.goal_state = None            # Goal state (State object)
    self.actions = []                 # list of actions (Action objects)

  ### Start running
  def start(self):
    self.running = True
    
  ### Stop running
  def stop(self):
    self.running = False

  ### Called every tick. Executes the plan if there is one
  def update(self, delta = 0):
    result = False # default return value
    if self.running and len(self.the_plan) > 0:
      # I have a plan, so execute the first action in the plan
      self.the_plan[0].agent = self
      result = self.the_plan[0].execute(delta)
      if result == False:
        # action failed
        print("AGENT FAILED")
        self.the_plan = []
      elif result == True:
        # action succeeded
        done_action = self.the_plan.pop(0)
        print("ACTION", done_action.name, "SUCCEEDED")
        done_action.reset()
    # If the result is None, the action is still executing
    return result

  ### Call back from Action class. Pass through to world
  def check_preconditions(self, preconds):
    if self.world is not None:
      return self.world.check_preconditions(preconds)
    return False

  ### Call back from Action class. Pass through to world
  def get_x_y_for_label(self, label):
    if self.world is not None:
      return self.world.get_x_y_for_label(label)
    return None

  ### Call back from Action class. Pass through to world
  def trigger(self, action):
    if self.world is not None:
      return self.world.trigger(action)
    return False

  ### Generate a plan. Init and goal are State objects. Actions is a list of Action objects
  ### Return the plan and the closed list
  def astar(self, init, goal, actions):
      plan = []    # the final plan
      open = []    # the open list (priority queue) holding State objects
      closed = []  # the closed list (already visited states). Holds state objects
      ### YOUR CODE GOES HERE
      current = init
      planList = []
      while not is_goal(current, goal):
        if not state_in_set(current, closed):
          closed.append(current) 
          for action in actions:
            flag = True
            for precondition in action.preconditions:
              if precondition not in current.propositions:
                flag = False
            if flag:
              cur = copy.deepcopy(current)
              cur.propositions = cur.propositions | action.add_list
              cur.propositions = cur.propositions - action.delete_list
              planTemp = planList + [action]
              open.append((cur,action, planTemp))
        open.sort(key = lambda x: x[0].get_f())
        temp = open.pop(0)
        current = temp[0]
        planList = temp[2]
      plan = planList
      ### CODE ABOVE
      return plan, closed

 

  ### Compute the heuristic value of the current state using the HSP technique.
  ### Current_state and goal_state are State objects.
  def compute_heuristic(self, current_state, goal_state, actions):
    actions = copy.deepcopy(actions)  # Make a deep copy just in case
    h = 0                             # heuristic value to return
    ## self, name, preconditions, add_list, delete_list, cost = 1
    ### YOUR CODE BELOW

    ## Creating dummy nodes and actionNodes list 
    dummyStart = Action('DummyStart', '', current_state.propositions, 'Dummy')
    dummyGoal = Action('DummyGoal', goal_state.propositions,'Dummy', 'Dummy')
    actionNodes = [dummyStart] + actions + [dummyGoal]
    ## creating edges list
    edges = []
    for n, actionNode1 in enumerate(actionNodes):
      for i, actionNode2 in enumerate(actionNodes):
        if n != i:
          for prop in actionNode1.add_list.intersection(actionNode2.preconditions):
            edges.append((actionNode1, prop, actionNode2))
    ## Walking on the graph
    visitedSet = set()
    queue = []
    queue.append(dummyStart)
    distanceDict = {}
    while (not len(queue) == 0):
      current = queue.pop()
      visitedSet.add(current)
      if current.name == 'DummyStart':
        current.cost = 0
        current_value = 0
      else:
        current_value = distanceDict[max(current.preconditions, key = lambda x: distanceDict[x])]
      for p in current.add_list:
        distanceDict[p] =  current_value + current.cost
      ## successors
      for action in actionNodes:
        if isActionSatisfied(action, edges, visitedSet):
          queue.append(action)
          actionNodes.remove(action)
    
    h = distanceDict[max(goal_state.propositions, key = lambda x: distanceDict[x])]
    
    ### YOUR CODE ABOVE
    return h

