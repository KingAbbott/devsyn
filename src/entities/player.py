import __builtin__

from pandac.PandaModules import *
from entities import Entity

base = __builtin__.base

class Player(Entity):
  speed = 50
  FORWARD = Vec3(0,2,0) # faster forward than backward
  BACK = Vec3(0,-1,0)
  LEFT = Vec3(-1,0,0)
  RIGHT = Vec3(1,0,0)
  STOP = Vec3(0)
  walk = STOP
  strafe = STOP
  ready_to_jump = False
  jump = 0

  def __init__(self, model):
    Entity.__init__(self, model)
    self.create_collisions()

    base.taskMgr.add(self.move_update, 'player-move-task')
    #base.taskMgr.add(self.jump_update, 'player-jump-task')

  def create_collisions(self):
    """ create collision solid and ray for the player """
    # floor collisions
    ray = CollisionRay()
    ray.setOrigin(0, 0, 1)
    ray.setDirection(0, 0, -1)
    cn = CollisionNode('player-ray')
    cn.addSolid(ray)
    cn.setFromCollideMask(BitMask32.bit(0))
    cn.setIntoCollideMask(BitMask32.allOff())
    solid = self.prime.attachNewNode(cn)
    self.node_ground_handler = CollisionHandlerQueue()
    base.cTrav.addCollider(solid, self.node_ground_handler)

  def activate(self):
    self.accept_controls()

  def deactivate(self):
    self.ignore_controls()

  def accept_controls(self):
    """ attach key events """
    self.accept("space", self.__setattr__, ["ready_to_jump", True])
    self.accept("space-up", self.__setattr__, ["ready_to_jump", False])
    self.accept("s", self.__setattr__, ["walk", self.STOP])
    self.accept("w", self.__setattr__, ["walk", self.FORWARD])
    self.accept("s", self.__setattr__, ["walk", self.BACK])
    self.accept("s-up", self.__setattr__, ["walk", self.STOP])
    self.accept("w-up", self.__setattr__, ["walk", self.STOP])
    self.accept("a", self.__setattr__, ["strafe", self.LEFT])
    self.accept("d", self.__setattr__, ["strafe", self.RIGHT])
    self.accept("a-up", self.__setattr__, ["strafe", self.STOP])
    self.accept("d-up", self.__setattr__, ["strafe", self.STOP])

  def ignore_controls(self):
    """ detach key events """
    self.ignore("space")
    self.ignore("space-up")
    self.ignore("s")
    self.ignore("w")
    self.ignore("s")
    self.ignore("s-up")
    self.ignore("w-up")
    self.ignore("a")
    self.ignore("d")
    self.ignore("a-up")
    self.ignore("d-up")

  def move_update(self, task):
    """ this task makes the player move """
    # move where the keys set it
    self.setPos(self.prime, self.walk * globalClock.getDt() * self.speed)
    self.setPos(self.prime, self.strafe * globalClock.getDt() * self.speed)
    return task.cont

  def jump_update(self, task):
    """ this task simulates gravity and makes the player jump """
    # get the highest Z from the down casting ray
    highestZ = -100
    for i in range(self.node_ground_handler.getNumEntries()):
      entry = self.node_ground_handler.getEntry(i)
      z = entry.getSurfacePoint(render).getZ()
      if z > highestZ and entry.getIntoNode().getName() == "Cube":
        highestZ = z

    # gravity effects and jumps
    self.setZ(self.getZ() + self.jump * globalClock.getDt())
    self.jump -= 1 * globalClock.getDt()
    if highestZ > self.getZ() - 0.3:
      self.jump = 0
      self.setZ(highestZ + 0.3)
      if self.ready_to_jump:
        self.jump = 1

    return task.cont
