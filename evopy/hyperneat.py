import evopy.abstract as abstract
import evopy.neat as neat

import numpy
import math

def sigmoid_activate(val):
    return 1.0/(1.0+math.exp(-4.9*val))

class Substrate:
    """
    abstract substrate class
    """
    def load_input(self,inps):
        pass
    def generate_weights(self,phenome):
        pass
    def run_net(self,inp):
        pass
    
class SheetSubstrate(Substrate):
    """
    Substrate that consists of multiple layers of nodes in a 2d grid
    """
    def __init__(self,layers):
        self.vectorized_activation = numpy.vectorize(sigmoid_activate)
        self.nodes=[]

        self.nodeloc=[]      
        self.bias=[]
        self.weights=[]
        for (width,height) in layers:
            self.nodes.append(numpy.zeros((width,height)))
            self.bias.append(numpy.zeros((width,height)))
            self.nodeloc.append(numpy.zeros((width,height,3)))
    
        for x in range(len(layers)-1):
            self.weights.append(numpy.zeros((layers[x+1][0]*layers[x+1][1],layers[x][0]*layers[x][1])))

        self.set_locations()
        
    def set_locations(self):
        x=(-1.0)
        y=(-1.0)
        z=(-1.0)
        zs=2.0/len(self.weights)
        for k in range(len(self.nodeloc)):
            (lw,lh) = self.nodes[k].shape
            xs=2.0/(lw-1)
            ys=2.0/(lh-1)
            x=(-1.0)
            for i in range(lw):
                y=(-1.0)
                for j in range(lh):
                    self.nodeloc[k][i,j][0]=x
                    self.nodeloc[k][i,j][1]=y
                    self.nodeloc[k][i,j][2]=z
                    y+=ys
                x+=xs
            z+=zs 
                    
    def generate_biases(self,phenome):
        x=(-1.0)
        y=(-1.0)
        z=(-1.0)
        zs=2.0/len(self.weights)
        for k in range(1,len(self.nodes)):
            (lw,lh) = self.nodes[k].shape
            xs=2.0/(lw-1)
            ys=2.0/(lh-1)
            z+=zs
            x=(-1.0)
            for i in numpy.arange(lw):
                y=(-1.0)
                for j in numpy.arange(lh):
                    self.bias[k][i,j]=phenome.run_inputs([x,y,z,x,y,z,0.0,1.0])[1]
                    y+=ys
                x+=xs

    def generate_weights(self,phenome):
        self.generate_biases(phenome)

        inp_vector=numpy.zeros((8))
        inp_vector[7]=1.0    

        zs=2.0/len(self.weights)
        
        for k in range(len(self.weights)):
            (l1w,l1h)=self.nodes[k].shape
            (l2w,l2h)=self.nodes[k+1].shape
            index1=0
            index2=0
            for i1 in range(l1w):
                for j1 in range(l1h):
                    for i2 in range(l2w):
                        for j2 in range(l2h):
                            inp_vector[0:3]=self.nodeloc[k][i1,j1]
                            inp_vector[3:6]=self.nodeloc[k+1][i2,j2]
                            delta = inp_vector[3:6]-inp_vector[0:3]
                            delta*=delta
                            inp_vector[6]=math.sqrt(sum(delta))
                            self.weights[k][index2,index1]=phenome.run_inputs(inp_vector)[0]
                            index2+=1
                    index2=0
                    index1+=1
                    
    def load_input(self,inp):
        self.nodes[0][:,:]=inp

    def run_net(self,inp):
        self.load_input(inp)
        for k in range(len(self.weights)):
            innodes = self.nodes[k].reshape((self.nodes[k].shape[0]*self.nodes[k].shape[1],1))
            outnodes = self.nodes[k+1].ravel()
            outnodes[:]=numpy.dot(self.weights[k],innodes).ravel()
            outnodes[:]=self.vectorized_activation(outnodes)
        hinode = outnodes.argmax()
        #x=hinode % outnodes.shape[0]
        #y=hinode / outnodes.shape[1]
        return (hinode,)

class HyperNEATPhenome(abstract.Phenome):
    substrate = SheetSubstrate([[5,6],[5,6],[5,6]])
    def __init__(self,genome):
        self.np = neat.NEATPhenome(genome)
        self.sub = HyperNEATPhenome.substrate
        self.sub.generate_weights(self.np)
    def run_inputs(self,inp):
        return self.sub.run_net(inp)

class HyperSimpleDomain(abstract.Domain):
    def __init__(self):
        self.inputs = numpy.zeros((5,6))
        #self.inputs[5,6]=1.5
    def run_phenome(self,phenome):
        return sum(phenome.run_inputs(self.inputs))


  
neat.NEATGenome.num_inp = 8
neat.NEATGenome.num_out = 2
a=abstract.SpeciatedPopulation(20,neat.NEATGenome,HyperSimpleDomain,HyperNEATPhenome)
a.run(1)
