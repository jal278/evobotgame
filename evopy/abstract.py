import copy
import random
import math

class Genome:
    """
    Abstract Genome Class (to be subclassed)
    Genome contains genetic representation
    Genomes should implement mutate, crossover, and genomic_distance (if speciation is desired)
    """
    def __init__(self):
        pass
    def mutate(self):
        pass
    def crossover(self,other):
        pass
    def genomic_distance(self,other):
        pass
    def __cmp__(self, other):
        return cmp(self.adjusted_fitness,other.adjusted_fitness)
    def __cmpreal__(self,other):
        return cmp(self.fitness,other.fitness)

class Phenome:
    """
    Abstract Phenome Class (to be subclassed)
    Phenome is realization of Genome (e.g. Neural Net for NEAT Genome)
    Phenomes should implement run_inputs
    """
    def __init__(self,genome):
        pass
    def run_inputs(self,inp):
        pass

class Domain:
    """
    Abstract Domain Class (to be subclassed)
    Domain will assign fitness to phenomes
    Domains should implement run_phenome
    """
    def __init__(self):
        pass
    def run_phenome(self,phenome):
        pass

class Species:
    """
    Default Species Class (used with SpeciatedPopulation)
    NEAT-Style Species
    """
    speciation_threshold=4.0
    survival_threshold=0.3
    minSize=8
    youngAge=5

    def uniform_select(self):
        lower_bound=int(len(self.list)*Species.survival_threshold)
        return copy.deepcopy(random.choice(self.list[lower_bound:]))
    def tournament_select(self):
        x=random.choice(self.list)
        y=random.choice(self.list)
        if(x.fitness>y.fitness):
            return copy.deepcopy(x)
        else:
            return copy.deepcopy(y)
    def __init__(self,genome):
        self.prototype=genome
        self.list = [genome]
        self.age = 0
        self.select=self.uniform_select
    def inSpecies(self,genome):
        if(genome.genomic_distance(self.prototype)<Species.speciation_threshold):
            return True
        return False
    def addToSpecies(self,genome):
        self.list.append(genome)
    def endGen(self):
        self.age+=1
        if(len(self.list)>0):
            self.prototype=self.list[-1]
    def clearSpecies(self):
        self.list = []
    def totFit(self):
        self.total_fitness = sum (map(lambda x:x.fitness,self.list))
        return self.total_fitness
    def maxFit(self):
        return max(map(lambda x:x.fitness,self.list))
    def sortFit(self):
        self.list.sort()
  

class Population:
    """
    Default Population Class
    """
    mutateRate = 0.75
    crossoverRate = 0.4
    survival_threshold = 0.4
    def tournament_select(self):
        x=random.choice(self.pop)
        y=random.choice(self.pop)
        if(x.fitness>y.fitness):
            return copy.deepcopy(x)
        else:
            return copy.deepcopy(y)

    def uniform_select(self):
        lower_bound=int(len(self.pop)*Population.survival_threshold)
        return copy.deepcopy(random.choice(self.pop[lower_bound:]))

        
    def __init__(self,size,genome_class,domain_class,phenome_class):
        self.pop = []
        self.popsize = size
        self.genome = genome_class
	self.fitcurve=[]
        for x in range(size):
            self.pop.append(genome_class())
            self.pop[-1].randomize()
        self.domain = domain_class()
        self.phenome = phenome_class
        self.select = self.uniform_select

   
    def evaluate_pop(self):
        for x in range(self.popsize):
            phenome=self.phenome(self.pop[x])
            self.pop[x].fitness = self.domain.run_phenome(phenome)
	self.fitcurve.append(self.max_fit())

    def max_fit(self):
        return reduce(max,map(lambda k:k.fitness,self.pop))

    def remove_worst(self):
        self.pop.sort(cmp=Genome.__cmpreal__)
        del self.pop[0]

    def sort_population(self):
        self.pop.sort(cmp=Genome.__cmpreal__)

    def create_new(self):
        mom=self.select()
        dad=self.select()
        if(random.random()<Population.mutateRate):
            mom.mutate()
        if(random.random()<Population.mutateRate):
            dad.mutate()
        if(random.random()<Population.crossoverRate):
            return mom.crossover(dad)
        else:
            return mom
    
    def write_fitness_curve(self):
	a=open("fitnessout.dat","w")
	for x in self.fitcurve:
		a.write(str(x)+"\n")
	a.close()
   
    def generate_next_gen(self):
        nextpop = []
        
        self.pop.sort(cmp=Genome.__cmpreal__)
        popchamp=self.pop[-1]
        nextpop.append(popchamp)
        champs = 1
        
        for y in range(self.popsize-champs):
            nextpop.append(self.create_new())
            
        self.pop = nextpop
        
    def run_epoch(self):
        self.generate_next_gen()
        self.evaluate_pop()
     
    def run(self,gens=100):
        self.evaluate_pop()
        for x in range(gens):
            self.run_epoch()
            print self

    def __repr__(self):
        out=""
        out+="PopSize %d, MaxFit %f\n" % (len(self.pop),self.max_fit())
        return out

class SpeciatedPopulation(Population):
    """
    Default SpeciatedPopulation class, used for NEAT-style speciation
    """
    targetspecies = 8
    def __init__(self,size,genome_class,domain_class,phenome_class):
        Population.__init__(self,size,genome_class,domain_class,phenome_class)
        self.species = []
        
    def speciate(self):
        for x in self.species:
            x.clearSpecies()
            
        for x in self.pop:
            found=False
            for y in self.species:
                if y.inSpecies(x):
                    y.addToSpecies(x)
                    found=True
                    break
            if not found:
                self.species.append(Species(x))

        self.remove_empty_species()
        self.adjust_fit()
        map(lambda x:x.sortFit(),self.species)
        map(lambda x:x.endGen(),self.species)

        if(len(self.species)>SpeciatedPopulation.targetspecies):
            Species.speciation_threshold+=0.3
        elif(len(self.species)<SpeciatedPopulation.targetspecies):
            Species.speciation_threshold-=0.3
            
    def remove_worst(self):
        self.pop.sort(cmp=Genome.__cmp__)
        del self.pop[0]

    def create_new(self):
        species = self.choose_species()
        mom=species.select()
        dad=species.select()
        if(random.random()<SpeciatedPopulation.mutateRate):
            mom.mutate()
        if(random.random()<SpeciatedPopulation.mutateRate):
            dad.mutate()
        if(random.random()<SpeciatedPopulation.crossoverRate):
            return mom.crossover(dad)
        else:
            return mom
        
    def remove_empty_species(self):
        for x in range(len(self.species)-1,-1,-1):
            if(len(self.species[x].list)==0):
               self.species.pop(x)        

    def adjust_fit(self):
        #tot_fit = self.total_fitness
        for y in self.species:
            conv_factor = 1.0/len(y.list)
            for x in y.list:
                x.adjusted_fitness=x.fitness * conv_factor
            y.total_adjusted_fitness = sum(map(lambda k:k.adjusted_fitness,y.list))
        self.total_adjusted_fitness = sum(map(lambda k:k.adjusted_fitness,self.pop))
        
    def choose_species(self):
        tot = 0.0
        cutoff=random.uniform(0,self.total_adjusted_fitness)
        for y in self.species:
            tot+=y.total_adjusted_fitness
            if tot>cutoff:
                return y
        return self.species[-1]
    
    def generate_next_gen(self):
        nextpop = []
        champs = 0

        self.pop.sort(cmp=Genome.__cmpreal__)
        popchamp=self.pop[-1]
        
        for y in self.species:
            if len(y.list)>Species.minSize or y.age<Species.youngAge or popchamp in y.list:
                champs+=1
                nextpop.append(y.list[-1])
        
        for y in range(self.popsize-champs):
            nextpop.append(self.create_new())
           
        self.pop = nextpop
        
    def run_epoch(self):
        Population.run_epoch(self)
        self.speciate()
     
    def run(self,gens=100):
        self.evaluate_pop()
        self.speciate()
        for x in range(gens):
            self.run_epoch()
            print x,self.max_fit(),len(self.species)
        self.sort_population()
    
    def __repr__(self):
        out=""
        out+="PopSize %d, MaxFit %f, NumSpecies %d\n" % (len(self.pop),self.max_fit(),len(self.species))
        for x in self.species:
            out+="Species Size: %d, MaxFit %f, Age: %d\n" % (len(x.list),x.maxFit(),x.age)
        return out
