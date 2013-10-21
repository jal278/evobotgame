import copy
import math
import random
import cPickle as pickle
import evopy.abstract as abstract

def sigmoid_activate(val):
    return 1.0/(1.0+math.exp(-4.9*val))

def signed_sigmoid(val):
    return (sigmoid_activate(val)-0.5)*2.0

def abs_activate(val):
    return abs(val)

def sin_activate(val):
    return math.sin(val)

def gauss_activate(val):
    return math.exp(-(val*val))

def linear_activate(val):
    return val
    
def IsCyclic(connections,nodes):
    inDict=dict()
    outDict=dict()
    visited = []
    
    for x in nodes:
        inDict[x[1]]=[]
        outDict[x[1]]=[]
        
    for x in connections:
       inDict[x[1]].append(x[0])
       outDict[x[0]].append(x[1])


    found=True
    while(found):
        found=False
        for x in nodes:
            if(x[1] not in visited and len(inDict[x[1]])==0):
                found=True
                visited.append(x[1])
                for y in outDict[x[1]]:
                    index=inDict[y].index(x[1])
                    del inDict[y][index]
                    
    if len(visited)==len(nodes):
        return False
    return True

err_res = None

class NEATGenome(abstract.Genome):

    innovation_number = 100
    INPUT=0
    HIDDEN=1
    OUTPUT=2
    node_add_prob=0.02
    link_add_prob=0.1
    weight_mut_rate=0.7
    weight_mut_power=0.5
    reenable_rate=0.075
    link_tries=30
    weight_factor=2.0
    num_inp=3
    num_out=1

    activation_list = [signed_sigmoid,abs_activate,sin_activate,gauss_activate,linear_activate]
    default_activation = [signed_sigmoid]

    def clone(self):
      return copy.deepcopy(self)

    def save(self,fname):
      out_file=open(fname,"w")
      pickle.dump(self,out_file)
   
    @classmethod
    def load(cls,fname):
     in_file=open(fname)
     return pickle.load(in_file)

    def __init__(self,inp=None,out=None):
        self.fitness = 0.0
        self.adjusted_fitness = 0.0
        self.nodes = []
        self.connections = []
        self.num_inp=NEATGenome.num_inp
        if(inp!=None):
         self.num_inp=inp

        self.num_out=NEATGenome.num_out
        if(out!=None):
         self.num_out=out
        
    def randomize(self):
        nodecount=0
        nodes = []
        connections = []
        
        for x in range(self.num_inp):
            nodes.append((NEATGenome.INPUT,nodecount+x,linear_activate))
        nodecount+=self.num_inp
        
        for x in range(self.num_out):
            nodes.append((NEATGenome.OUTPUT,nodecount+x,NEATGenome.default_activation[0]))
            #nodes.append((NEATGenome.OUTPUT,nodecount+x,random.choice(NEATGenome.activation_list)))

        for x in range(self.num_inp):
            for y in range(self.num_out):
                connections.append((x,self.num_inp+y,random.uniform(-1.0,1.0),y+self.num_out*x,True))

        self.connections=connections
        self.nodes=nodes

    def disable_link(self,num):
        old_link = self.connections[num]
        new_link = (old_link[0],old_link[1],old_link[2],old_link[3],False)
        self.connections[num]=new_link

    def enable_link(self,num):
        old_link = self.connections[num]
        new_link = (old_link[0],old_link[1],old_link[2],old_link[3],True)
        self.connections[num]=new_link
        #if(IsCyclic(self.connections,self.nodes)):
        #    self.connections[num]=old_link
        
    def add_link(self,n1=None,n2=None,weight=None):
        if(n1==None):
            found=False
            for y in range(NEATGenome.link_tries):
                a=random.choice(self.nodes)
                b=random.choice(self.nodes)
                weight=random.uniform(-1.0,1.0)
                n1=a[1]
                n2=b[1]
                if(b[0]==NEATGenome.INPUT):
                    continue
                if(b[0]==NEATGenome.OUTPUT):
                    continue
                if(IsCyclic(self.connections+[(n1,n2,weight,NEATGenome.innovation_number,True)],self.nodes)):
                    continue
                dup=False
                for k in self.connections:
                    if k[0]==n1 and k[1]==n2:
                        dup=True
                        break
                if(dup):
                    continue
                found=True
                break
            if not found:
                return None
        self.connections.append((n1,n2,weight,NEATGenome.innovation_number,True))
        NEATGenome.innovation_number+=1
       
    def add_node(self):
        activation = random.choice(NEATGenome.activation_list)
        con_num=random.randint(0,len(self.connections)-1)
        split_con=self.connections[con_num]
        new_number=NEATGenome.innovation_number
        self.nodes.append((NEATGenome.HIDDEN,new_number,activation))
        self.disable_link(con_num)
        self.add_link(split_con[0],new_number,split_con[2])
        self.add_link(new_number,split_con[1],1.0)
        
    def mutate(self):
        for k in range(len(self.connections)):
            if(not self.connections[k][-1]):
                if(random.random()<NEATGenome.reenable_rate):
                    self.enable_link(k)
            if(random.random()<NEATGenome.weight_mut_rate):
                oldcon = self.connections[k]
                newweight = random.gauss(0,NEATGenome.weight_mut_power) + oldcon[2]
                newweight=max(newweight,-3.0)
                newweight=min(newweight,3.0)
                newcon = (oldcon[0],oldcon[1],newweight,oldcon[3],oldcon[4])
                self.connections[k]=newcon

        if(random.random()<NEATGenome.link_add_prob):
            self.add_link()

        if(random.random()<NEATGenome.node_add_prob):
            self.add_node()
        
    def crossover(self,other):
        global err_res
        child = NEATGenome()
        
        if(self.fitness>other.fitness):
            fitparent=self
            parent=other
        else:
            fitparent=other
            parent=self

        fi = 0
        f_inno = 0
        pi = 0
        p_inno = 0

        while(fi<len(fitparent.connections) and pi<len(parent.connections)):
            f_inno = fitparent.connections[fi][-2]
            p_inno = parent.connections[pi][-2]

            if(f_inno==p_inno):
                if(random.random()<0.5):
                    if(random.random()<0.5):
                        child.connections.append(parent.connections[pi])
                    else:
                        child.connections.append(fitparent.connections[fi])
                else:
                    x=parent.connections[pi]
                    y=fitparent.connections[fi]
                    new_weight=(x[2]+y[2])/2.0
                    child.connections.append((x[0],x[1],new_weight,x[3],x[4]))
                fi+=1
                pi+=1
            elif(f_inno<p_inno):
                child.connections.append(fitparent.connections[fi])
                fi+=1
            else:
                pi+=1

        while(fi<len(fitparent.connections)):
            child.connections.append(fitparent.connections[fi])
            fi+=1          
       
        child.nodes = fitparent.nodes

        if(IsCyclic(child.connections,child.nodes)):
            err_res=[child,fitparent,parent]
            raise "Cyclic bug?"
            return fitparent

        return child
        
    def genomic_distance(self,other):
        weight_diff = 0.0
        shared = 0.0
        disjoint = 0.0
        excess = 0.0

        si = 0
        s_inno = 0
        oi = 0
        o_inno = 0

        while(si<len(self.connections) and oi<len(other.connections)):
              s_inno=self.connections[si][-2]
              o_inno=other.connections[oi][-2]
              if(s_inno==o_inno):
                  shared+=1
                  weight_diff+=abs(self.connections[si][2]-other.connections[oi][2])
                  si+=1
                  oi+=1
              elif(s_inno<o_inno):
                  disjoint+=1
                  si+=1
              else:
                  disjoint+=1
                  oi+=1
        
        excess = max(len(self.connections)-si-1,len(other.connections)-oi-1)
                  
        return NEATGenome.weight_factor*weight_diff/shared+disjoint+excess

    def __repr__(self):
        out=""
        for x in self.nodes:
            out+="Node %d Type %d Activation %s\n" % (x[1],x[0],x[2].__name__)
        for x in self.connections:
            out+="Connection from %d to %d, weight %f, innovation %d, enabled %d\n" % (x[0],x[1],x[2],x[3],int(x[4]))
        out+="Fitness:%f, %f" % (self.fitness,self.adjusted_fitness) 
        return out

class CascadeGenome(NEATGenome):
    weight_mut_rate=0.6
    weight_mut_power=0.6
    node_add_prob=0.00
    link_add_prob=0.2
    
    def mutate(self):
        for k in range(len(self.connections)):
            if(self.connections[k][0]<self.num_inp and self.connections[k][1]!=(len(self.nodes)-1)):
                continue
            if(random.random()<CascadeGenome.weight_mut_rate):
                oldcon = self.connections[k]
                newweight = random.gauss(0,CascadeGenome.weight_mut_power) + oldcon[2]
                newweight=max(newweight,-3.0)
                newweight=min(newweight,3.0)
                newcon = (oldcon[0],oldcon[1],newweight,oldcon[3],oldcon[4])
                self.connections[k]=newcon

        if(random.random()<CascadeGenome.node_add_prob):
            self.add_node()
        if(random.random()<CascadeGenome.link_add_prob):
            self.add_cascade_link()
            
    def add_cascade_link(self):
        out_node=self.nodes[-1][1] #last added node's innovation number
        viable_nodes=map(lambda x:x[1],self.nodes[:-1])
        for k in self.connections:
            if k[0]==out_node:
                if k[1] in viable_nodes:
                    viable_nodes.remove(k[1])
            if k[1]==out_node:
                if k[0] in viable_nodes:
                    viable_nodes.remove(k[0])
        if len(viable_nodes)==0:
            return
        node=random.choice(viable_nodes)

        the_node=None
        for k in self.nodes:
            if k[1]==node:
                the_node=k

        if the_node==None:
            raise "error"

        if the_node[0]==NEATGenome.INPUT or the_node[0]==NEATGenome.HIDDEN:
            self.add_link(the_node[1],out_node,random.uniform(-1.0,1.0))
        elif the_node[0]==NEATGenome.HIDDEN:
            self.add_link(out_node,the_node[1],random.uniform(-1.0,1.0))
        
        
    def add_node(self):
        activation = random.choice(NEATGenome.activation_list)
        new_number=NEATGenome.innovation_number
        self.nodes.append((NEATGenome.HIDDEN,new_number,activation))

        num=random.randint(0,self.num_inp-1)
        self.add_link(new_number,num,random.uniform(-1.0,1.0))
        num=random.randint(0,self.num_out-1)
        self.add_link(new_number,num+self.num_inp,random.uniform(-1.0,1.0))
        """       
        for x in range(len(self.nodes)-1):
            if self.nodes[x][0]==NEATGenome.HIDDEN or self.nodes[x][0]==NEATGenome.INPUT:
                self.add_link(self.nodes[x][1],new_number,random.uniform(-1.0,1.0))
        for out in range(self.num_out):
            self.add_link(new_number,out+self.num_inp,random.uniform(-1.0,1.0))   
        """
        
class NEATNode:
    def __init__(self,node):
        self.type = node[0]
        self.number= node[1]
        self.af = node[2]
        self.activation = 0.0
        self.done=0.0
        self.connections = []
    def clear(self):
        self.activation = 0.0
        self.done=0.0
    def load(self,val):
        self.activation=val
        self.done=1.0
    def activate(self):
        self.activation=self.af(self.activation)
        self.done=True
    def get(self):
        return self.activation
    def add_connection(self,fromNode,weight):
        self.connections.append((fromNode,weight))

class NEATPhenome(abstract.Phenome):

    def __init__(self,genome):
        self.nodes = []
        self.inputs = []
        self.outputs = []
        self.hidden = []
        for x in genome.nodes:
            nodetype= x[0]
            newNode = NEATNode(x)

            self.nodes.append(newNode)
            
            if(nodetype==NEATGenome.INPUT):
                self.inputs.append(newNode)
            if(nodetype==NEATGenome.OUTPUT):
                self.outputs.append(newNode)
            else:
                self.hidden.append(newNode)
            
        for y in genome.connections:
            if(y[-1]):
                self.add_connection(y)
    
    def find_node(self,nn):
        for x in self.nodes:
            if x.number==nn:
                return x
        return None

    def add_connection(self,conn):
        start_node = self.find_node(conn[0])
        end_node = self.find_node(conn[1])
        weight = conn[2]
        end_node.add_connection(start_node,weight)
      
    def clear_network(self):
        for x in self.nodes:
            x.clear()
            
    def propogate_back(self,nodes,depth=0):
        if(depth>20):
            print "Cyclic error in propogation"
            return
        for x in nodes:
            for y in x.connections:
                if not y[0].done:
                    self.propogate_back([y[0],],depth+1)
                x.activation+=y[0].activation*y[1]
            x.activate()
            
        
    def run_inputs(self,inp):
        self.clear_network()
        
        for x in range(len(self.inputs)):
            self.inputs[x].load(inp[x])

        self.propogate_back(self.outputs)

        collected = map(lambda x:x.get(),self.outputs)
        return collected

    def __repr__(self):
        out=""
        for x in self.nodes:
            for y in x.connections:
                out += "%d to %d, with weight %f\n" % (y[0].number,x.number,y[1])
        return out
 
class XORDomain(abstract.Domain):
    def __init__(self):
        pass
    def run_phenome(self,phenome):
        test_patterns = [ ([0.0,0.0,1.0],[0.0]),
                          ([0.0,1.0,1.0],[1.0]),
                          ([1.0,0.0,1.0],[1.0]),
                          ([1.0,1.0,1.0],[0.0])]
        err=0.0
        for x in range(4):
            exp=test_patterns[x][1]
            res=phenome.run_inputs(test_patterns[x][0])
            err+=abs(exp[0]-res[0])
        err*=err
        return max(4.0-err,0.01)

def neat_test(gens=50):                           
    pop = abstract.SpeciatedPopulation(250,NEATGenome,XORDomain,NEATPhenome)
    pop.run(gens)
    return pop
