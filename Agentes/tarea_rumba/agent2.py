from mesa import Agent
import heapq

class RandomAgent(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
    """
    def __init__(self, unique_id, model,pos):
        
        super().__init__(unique_id, model)
        self.steps_taken = 0
        
        self.next_pos=[]
        self.energy=100
        self.charging_zones=[pos]
        self.state="cleaning"
        self.Matriz_recorridos=[[0 for _ in range(self.model.grid.height)] for _ in range(self.model.grid.width)]
        

    def Check_energy(self):
        if self.energy<=0:
            self.model.grid.remove_agent(self)
        else:
            return abs(self.charging_zones[0][0]-self.pos[0])+abs(self.charging_zones[0][1]-self.pos[1])<self.energy-7
            
    
    def go_to_charger(self):
        if self.charging_zones:
            Charging_station=self.charging_zones[0]
            path = self.a_star_search(self.pos, Charging_station)
            if path:
                if self.pos==Charging_station:
                   
                    self.state="Charging"
                elif self.state!="Charging":
                    self.model.grid.move_agent(self, path[1])# Move to the next position in the path
                    self.energy-=1
                    self.steps_taken += 1
                
                

          
    def a_star_search(self, start, goal):
        print("A*")
        print(start)
        print(goal)
        
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

            for neighbor in self.model.grid.iter_neighborhood(current, moore=True):
                

                # Check if the neighbor cell contains an obstacle
                cell_contents = self.model.grid.get_cell_list_contents(neighbor)
                if any(isinstance(obj, ObstacleAgent) for obj in cell_contents):
                    continue

                tentative_g_score = g_score[current] + 1  # Assuming cost between neighbors is 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None
    
    def Charging(self):
        if self.state=="Charging":
            
            this_cell=self.model.grid.get_cell_list_contents([self.pos])
            charger_cell=[obj for obj in this_cell if isinstance(obj,Charger)]
            if len(charger_cell)>0:
                Charger.charge(self)
                
     
    def Cleaning(self):
        
        Trash_moves=[]
        empty_moves = []
       
        # next_move = self.random.choice(next_moves)
        self.Matriz_recorridos[self.pos[0]][self.pos[1]]=1
        
        for neighbor in self.model.grid.iter_neighborhood(self.pos, moore=True):
        
            get_cont = self.model.grid.get_cell_list_contents(neighbor)
            
            if not get_cont:
                empty_moves.append(neighbor)
                self.Matriz_recorridos[neighbor[0]][neighbor[1]]=1
                
            elif isinstance(get_cont[0],Charger):
                pass  
                  
            elif isinstance(get_cont[0],Trash) and not len(get_cont)>1:
                Trash_moves.append(neighbor)

        # Now move:
        if Trash_moves:
            
            self.model.grid.move_agent(self, self.random.choice(Trash_moves))
            self.state="clean"
            self.energy-=1
            self.steps_taken += 1
            
        elif empty_moves:
            not_visited=[]
            for move in empty_moves:
                if self.Matriz_recorridos[move[0]][move[1]]==0:
                    not_visited.append(move)
                    
            if not_visited:
                self.model.grid.move_agent(self, self.random.choice(not_visited))
                self.energy-=1
                self.steps_taken += 1
            else:
                self.model.grid.move_agent(self, self.random.choice(empty_moves))
                self.energy-=1
                self.steps_taken += 1
                
        else:
            next_move = self.pos
            self.model.grid.move_agent(self, next_move)

    def clean(self):
        this_cell=self.model.grid.get_cell_list_contents([self.pos])
        trash_cell=[obj for obj in this_cell if isinstance(obj,Trash)]
        
        if len(trash_cell)>0 and self.Check_energy():
            delete_trash=self.random.choice(trash_cell)
            self.model.grid.remove_agent(delete_trash)
            self.energy-=5
            self.state="cleaning"
            self.Matriz_recorridos[self.pos[0]][self.pos[1]]=1
        else:
            self.state="cleaning"
            

    def step(self):
        
        if self.Check_energy()==False and self.state!="Charging":
            self.state="Going_to_Charger"
            
            
        state=self.state
        print(state)
        if state=="cleaning":
            self.Cleaning()
        elif state=="Going_to_Charger":
            self.go_to_charger()
        elif state=="Charging":
            self.Charging()
        elif state=="clean":
            self.clean()
            

class ObstacleAgent(Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass  
    
class Trash(Agent):
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        
    def step(self):
        pass
    
class Charger(Agent):
    
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        
    def charge(agent):
        agent.energy+=10
        if agent.energy>=100:
            agent.energy=100
            agent.state="cleaning"
        