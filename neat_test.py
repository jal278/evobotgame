from evopy.neat import *

class ANDDomain(abstract.Domain):
    def __init__(self):
        pass
    def run_phenome(self,phenome):
        test_patterns = [ ([0.0,0.0,1.0],[0.0]),
                          ([0.0,1.0,1.0],[0.0]),
                          ([1.0,0.0,1.0],[0.0]),
                          ([1.0,1.0,1.0],[1.0])]
        err=0.0
        for x in range(4):
            exp=test_patterns[x][1]
            res=phenome.run_inputs(test_patterns[x][0])
            err+=abs(exp[0]-res[0])
        err*=err
        return max(4.0-err,0.01)


#pop = abstract.SpeciatedPopulation(250,NEATGenome,ORDomain,NEATPhenome)
#pop.run(250)

domain=ANDDomain()
genome=NEATGenome(3,1)
genome.randomize()
#genome=NEATGenome.load("or_solution")

phenome=NEATPhenome(genome)
fitness=domain.run_phenome(phenome)

iteration=0
while fitness<3.9:
 iteration+=1

 new_genome=genome.clone()
 new_genome.mutate()
 new_phenome=NEATPhenome(new_genome)
 new_fitness=domain.run_phenome(new_phenome)

 if(new_fitness > fitness):
   print iteration,new_fitness
   fitness=new_fitness
   genome=new_genome

print "Solved in %d iterations" % iteration
genome.save("or_solution")
