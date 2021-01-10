from lview import *
from time import time
import itertools, math
from commons import prediction
from copy import copy

lview_script_info = {
	"script": "Drawings",
	"author": "leryss",
	"description": "Draws indicators for different things"
}

turret_ranges   = False
minion_last_hit = False
attack_range    = False

skillshots      = False
skillshots_predict = False
skillshots_min_range = 0
skillshots_max_speed = 0

ignore_missiles = set([
	"viefx", "viqmissile", "virmissile",
	"missfortunericochetshotdud",
	"threshqpullmissile"
])

def lview_load_cfg(cfg):
	global turret_ranges, minion_last_hit, attack_range
	global skillshots, skillshots_predict, skillshots_min_range, skillshots_max_speed
	turret_ranges        = cfg.get_bool("turret_ranges", True)
	minion_last_hit      = cfg.get_bool("minion_last_hit", True)
	attack_range         = cfg.get_bool("attack_range", True)
	                     
	skillshots           = cfg.get_bool("skillshots", True)
	skillshots_predict   = cfg.get_bool("skillshots_predict", True)
	skillshots_min_range = cfg.get_float("skillshots_min_range", 500)
	skillshots_max_speed = cfg.get_float("skillshots_max_speed", 2500)
	
def lview_save_cfg(cfg):
	global turret_ranges, minion_last_hit, attack_range
	global skillshots, skillshots_predict, skillshots_min_range, skillshots_max_speed
	cfg.set_bool("turret_ranges",         turret_ranges)
	cfg.set_bool("minion_last_hit",       minion_last_hit)
	cfg.set_bool("attack_range",          attack_range)
	
	cfg.set_bool("skillshots",            skillshots)
	cfg.set_bool("skillshots_predict",    skillshots_predict)
	cfg.set_float("skillshots_min_range", skillshots_min_range)
	cfg.set_float("skillshots_max_speed", skillshots_max_speed)
	
def lview_draw_settings(game, ui):
	global turret_ranges, minion_last_hit, attack_range
	global skillshots, skillshots_predict, skillshots_min_range, skillshots_max_speed
	turret_ranges   = ui.checkbox("Turret ranges", turret_ranges)
	minion_last_hit = ui.checkbox("Minion last hit", minion_last_hit)
	attack_range    = ui.checkbox("Champion attack range", attack_range)
	
	ui.separator()
	ui.text("Skillshots")
	skillshots           = ui.checkbox("Draw skillshots", skillshots)
	skillshots_predict   = ui.checkbox("Use skillshot prediction", skillshots_predict)
	skillshots_min_range = ui.dragfloat("Minimum skillshot range", skillshots_min_range, 100, 0, 3000)
	skillshots_max_speed = ui.dragfloat("Maximum skillshot speed", skillshots_max_speed, 100, 1000, 4000)
	

def draw_rect(game, start_pos, end_pos, radius, color):
	
	dir = Vec3(end_pos.x - start_pos.x, 0, end_pos.z - start_pos.z).normalize()
				
	left_dir = Vec3(dir.x, dir.y, dir.z).rotate_y(90).scale(radius)
	right_dir = Vec3(dir.x, dir.y, dir.z).rotate_y(-90).scale(radius)
	
	p1 = Vec3(start_pos.x + left_dir.x,  start_pos.y + left_dir.y,  start_pos.z + left_dir.z)
	p2 = Vec3(end_pos.x + left_dir.x,    end_pos.y + left_dir.y,    end_pos.z + left_dir.z)
	p3 = Vec3(end_pos.x + right_dir.x,   end_pos.y + right_dir.y,   end_pos.z + right_dir.z)
	p4 = Vec3(start_pos.x + right_dir.x, start_pos.y + right_dir.y, start_pos.z + right_dir.z)
	
	game.draw_rect_world(p1, p2, p3, p4, 3, color)

def draw_atk_range(game, player):
	color = Color.GREEN
	color.a = 0.5
	game.draw_circle_world(player.pos, player.base_atk_range + player.gameplay_radius, 100, 2, color)

def draw_turret_ranges(game, player):
	color = Color.RED
	color.a = 0.5
	for turret in game.turrets:
		if turret.is_alive and turret.is_enemy_to(player) and game.is_point_on_screen(turret.pos):
			range = turret.base_atk_range + turret.gameplay_radius
			game.draw_circle_world(turret.pos, range, 100, 2, color)
			dist = turret.pos.distance(player.pos) - range
			if dist <= player.gameplay_radius:
				game.draw_circle_world(player.pos, player.gameplay_radius*2, 30, 3, Color.RED)

def draw_minion_last_hit(game, player):
	color = Color.CYAN
	for minion in game.minions:
		if minion.is_alive and minion.is_enemy_to(player) and game.is_point_on_screen(minion.pos):
			if prediction.is_last_hitable(game, player, minion):
				p = game.hp_bar_pos(minion)
				game.draw_rect(Vec4(p.x - 33, p.y - 8, p.x + 33, p.y), Color.GREEN)

def draw_skillshots(game, player):
	global ignore_missiles
	global skillshots, skillshots_predict, skillshots_min_range, skillshots_max_speed
	
	for missile in game.missiles:
		
		if missile.has_tags(SpellFlag.Targeted) or missile.speed > skillshots_max_speed or missile.range < skillshots_min_range or missile.name in ignore_missiles:
			continue
			
		end_pos = missile.end_pos.clone()
		start_pos = missile.start_pos.clone()
		curr_pos = missile.pos.clone()
		impact_pos = None
		
		start_pos.y = game.map.height_at(start_pos.x, start_pos.z) + missile.height
		end_pos.y = start_pos.y
		curr_pos.y = start_pos.y
		
		if missile.radius > 0:
			draw_rect(game, curr_pos, end_pos, missile.radius, Color.WHITE)
			game.draw_circle_world_filled(curr_pos, missile.radius, 20, Color.RED)
	
		if missile.impact_radius > 0:
			r = missile.impact_radius
			end_pos.y = game.map.height_at(end_pos.x, end_pos.z)
			percent_done = missile.start_pos.distance(curr_pos)/missile.start_pos.distance(end_pos)
			color = Color(1, 1.0 - percent_done, 0, 0.5)
			
			game.draw_circle_world(end_pos, r, 30, 3, Color.WHITE)
			game.draw_circle_world_filled(end_pos, r*percent_done, 30, color)
	
def lview_update(game, ui):
	global turret_ranges, minion_last_hit, attack_range, skillshots
	
	player = game.player

	if attack_range and game.is_point_on_screen(player.pos):
		draw_atk_range(game, player)
	
	if turret_ranges:
		draw_turret_ranges(game, player)
					
	if minion_last_hit:
		draw_minion_last_hit(game, player)
				
	if skillshots:
		draw_skillshots(game, player)
					
				