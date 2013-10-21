import evopy.abstract as abstract
import random

class FloatGenome(abstract.Genome):
    mutateChance=0.3
    mutatePower=0.2
    def __init__(self,size=10):
        self.genes = []
        self.fitness = 0.0
        self.adjusted_fitness = 0.0
        self.size=size
    def randomize(self):
        for x in range(self.size):
            self.genes.append(random.random())
    def mutate(self):
        for x in range(self.size):
            if random.random()>FloatGenome.mutateChance:
                self.genes[x]=self.genes[x]+random.uniform(-FloatGenome.mutatePower,FloatGenome.mutatePower)
                if(self.genes[x]>1.0):
                    self.genes[x]=1.0
                if(self.genes[x]<0.0):
                    self.genes[x]=0.0
    def crossover(self,other):
        x=FloatGenome(self.size)
        for y in range(self.size):
            if random.random()>0.5:
                x.genes.append(self.genes[y])
            else:
                x.genes.append(other.genes[y])
        return x
    def genomic_distance(self,other):
        diff = 0.0
        for y in range(self.size):
            diff+=abs(self.genes[y]-other.genes[y])
        return diff
    
class SimplePhenome(abstract.Phenome):
    def __init__(self,genome):
        self.genes = genome.genes
    def run_inputs(self,inp):
        return self.genes
    
class SimpleDomain(abstract.Domain):
    def __init__(self):
        pass
    def run_phenome(self,phenome):
        return sum(phenome.run_inputs([1.0,0.0,1.0]))
    
def simple_test(gens=50):
    pop = abstract.Population(250,FloatGenome,SimpleDomain,SimplePhenome)
    pop.run(gens)
    return pop
