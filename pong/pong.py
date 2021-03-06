import sys
import pypong
import pongrunner
from evopy.neat import *

#interface into the pong player type
class ANNPlayer(object):
  def __init__(self,phenome):
   self.ann=phenome
  
  def update(self, paddle, game):
   centery = float(paddle.rect.centery) / (game.bounds.bottom)
   bally = float(game.ball.rect.centery) / (game.bounds.bottom)
   inputs=[centery,centery-bally,1.0] 

   self.ann.load_inputs(inputs)
   self.ann.run_step()
   output=self.ann.get_outputs()[0]
   #print output
 
   if(output>0.3):
    paddle.direction=1
   elif(output<-0.3):
    paddle.direction=-1
   else:
    paddle.direction=0

  def hit(self):
       pass

  def lost(self):
       pass
        
  def won(self):
       pass

  def reset(self):
       pass
    
#neat domain for pong
class PongDomain(abstract.Domain):
    def __init__(self):
        pass

    def run_phenome(self,phenome):
       results=[0,0]
       for x in range(5):
        phenome.clear_network()
        netplayer=ANNPlayer(phenome)
        opponent= pongrunner.BasicAIPlayer()
        temp=pongrunner.run(netplayer,opponent,False,x)
        results[0]+=temp[0]
        results[1]+=temp[1]
       score=results[0]-results[1]
       return max(0.01,score+50)


evolve=False

if(len(sys.argv)>1 and sys.argv[1]=='evolve'):
 evolve=True

pop = abstract.SpeciatedPopulation(200,NEATGenome,PongDomain,NEATPhenome)
domain = PongDomain()
champ=None

if(evolve):
 NEATGenome.num_inputs=3
 NEATGenome.num_outputs=1
 pop.run(100)
 champ=pop.pop[-1]
 champ.save("pop_champ")
else:
 champ=NEATGenome.load("pop_champ")

champ_phenome=NEATPhenome(champ)
player=ANNPlayer(champ_phenome)
print domain.run_phenome(champ_phenome)

print pongrunner.run(player,pongrunner.BasicAIPlayer(),False,1)
pongrunner.run(player,pongrunner.BasicAIPlayer(),True,1)
