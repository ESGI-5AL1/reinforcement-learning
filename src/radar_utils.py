

from qlearning.qlearning_consts import RADAR_RANGE, RADAR_RANGE_CHECKPOINT, RADAR_RANGE_FLAG


def compute_ennemy_position(game, player_x, player_y, radar, enemy_detected):
    HEIGHT_THRESHOLD = 10
    
    for enemy in game.enemy_list:
        dx = enemy.center_x - player_x
        dy = enemy.center_y - player_y
        
        
        if abs(dy) < HEIGHT_THRESHOLD:
            distance = abs(dx) 
            
            if distance < RADAR_RANGE:
                enemy_detected = True
                radar['enemy_E' if dx > 0 else 'enemy_W'] = True
                
    return enemy_detected

def compute_flag_positon(self,player_x,player_y,radar):
        flag = self.scene["Flag"][0]
        dx = flag.center_x - player_x
        dy = flag.center_y - player_y

        distance_to_flag = (dx**2 + dy**2)**0.5
        radar['flag_east'] = dx > 0
        flag_detected = distance_to_flag < RADAR_RANGE_FLAG
        radar['flag_close'] = flag_detected

def compute_checkpoint_position(self,player_x,player_y,radar):
    if len(self.scene["Checkpoint"]) > 0:  
            checkpoint = self.scene["Checkpoint"][0]
            dx = checkpoint.center_x - player_x
            dy= checkpoint.center_y -player_y
            distance_to_checkpoint = (dx**2 + dy**2)**0.5
            radar['checkpoint_east'] = dx > 0
            radar['checkpoint_close'] = distance_to_checkpoint < RADAR_RANGE_CHECKPOINT
    else:
            radar['checkpoint_east'] = False
            radar['checkpoint_close'] = False         
