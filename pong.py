import pypong
import pongrunner
from evopy.neat import *

class ANNPlayer(object):
  def __init__(self,phenome):
   self.ann=phenome
  
  def update(self, paddle, game):
   centery = float(paddle.rect.centery) / (game.bounds.bottom)
   bally = float(game.ball.rect.centery) / (game.bounds.bottom)
   inputs=[centery,centery-bally,1.0] 

   output=self.ann.run_inputs(inputs)[0]
 
   if(output>0.7):
    paddle.direction=1
   elif(output<0.3):
    paddle.direction=-1
   else:
    paddle.direction=0

  def hit(self):
       pass

  def lost(self):
       pass
        
  def won(self):
       pass
    

class PongDomain(abstract.Domain):
    def __init__(self):
        pass

    def run_phenome(self,phenome):
       results=[0,0]
       for x in range(3):
        netplayer=ANNPlayer(phenome)
        opponent= pongrunner.BasicAIPlayer()
        temp=pongrunner.run(netplayer,opponent,False)
        results[0]+=temp[0]
        results[1]+=temp[1]
       score=results[0]-results[1]
       return max(0.01,score+50)

"""
NEATGenome.num_inputs=3
NEATGenome.num_outputs=1
pop = abstract.SpeciatedPopulation(100,NEATGenome,PongDomain,NEATPhenome)
pop.run(20)
"""

#champ=pop.pop[-1]
#champ.save("pop_champ")
champ=NEATGenome.load("pop_champ")
champ_phenome=NEATPhenome(champ)

player=ANNPlayer(champ_phenome)
#pongrunner.run(player,pongrunner.BasicAIPlayer(),True)
pongrunner.run(player,pongrunner.MousePlayer(pongrunner.input_state),True)
