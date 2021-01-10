from lview import *
import json

lview_script_info = {
	"script": "Vision Tracker",
	"author": "leryss",
	"description": "Tracks enemy invisible objects and clones"
}

show_clones, show_wards, show_traps = None, None, None

traps = {
	#Name -> (radius, show_radius_circle, show_radius_circle_minimap)                      
	'caitlyntrap'          : [50,  True, False],
	'dominationscout'      : [0,   False, False],
	'jhintrap'             : [140, True, False],
	'jinxmine'             : [50,  True, False],
	'maokaisproutling'     : [50,  False, False],
	'nidaleespear'         : [50,  True, False],
	'shacobox'             : [300, True, False],
	'teemomushroom'        : [75,  True, True]
}

wards = {
	'bluetrinket'          : [900, True, True],
	'jammerdevice'         : [900, True, True],
	'perkszombieward'      : [900, True, True],
	'sightward'            : [900, True, True],
	'visionward'           : [900, True, True],
	'yellowtrinket'        : [900, True, True],
	'yellowtrinketupgrade' : [900, True, True],
	'ward'                 : [900, True, True],
}

clones = {
	'shaco'           : [0, False, False],
	'leblanc'         : [0, False, False],
	'monkeyking'      : [0, False, False],
	'neeko'           : [0, False, False],
	'fiddlesticks'    : [0, False, False],
}


def lview_load_cfg(cfg):
	global show_clones, show_wards, show_traps, traps, wards

	show_clones = cfg.get_bool("show_clones", True)
	show_wards = cfg.get_bool("show_wards", True)
	show_traps = cfg.get_bool("show_traps", True)
	
	traps = json.loads(cfg.get_str("traps", json.dumps(traps)))
	wards = json.loads(cfg.get_str("wards", json.dumps(wards)))
	
def lview_save_cfg(cfg):
	global show_clones, show_wards, show_traps, traps, wards
	
	cfg.set_bool("show_clones", show_clones)
	cfg.set_bool("show_wards", show_wards)
	cfg.set_bool("show_traps", show_traps)
	
	cfg.set_str("traps", json.dumps(traps))
	cfg.set_str("wards", json.dumps(wards))
	
def lview_draw_settings(game, ui):
	global traps, wards
	global show_clones, show_wards, show_traps
	
	show_clones = ui.checkbox("Show clones", show_clones)
	show_wards = ui.checkbox("Show wards", show_wards)
	show_traps = ui.checkbox("Show clones", show_traps)
	
	ui.text("Traps")
	for x in traps.keys():
		if ui.treenode(x):
			traps[x][1] = ui.checkbox("Show range circles", traps[x][1])
			traps[x][2] = ui.checkbox("Show on minimap", traps[x][2])
			
			ui.treepop()
			
	ui.text("Wards")
	for x in wards.keys():
		if ui.treenode(x):
			wards[x][1] = ui.checkbox("Show range circles", wards[x][1])
			wards[x][2] = ui.checkbox("Show on minimap", wards[x][2])
			
			ui.treepop()

def draw(game, obj, radius, show_circle_world, show_circle_map):
			
	sp = game.world_to_screen(obj.pos)
	txt = obj.name
	duration = obj.duration + obj.last_visible_at - game.time
	if duration > 0:
		txt += f' {duration:.0f}'
	game.draw_button(sp, txt, Color.WHITE, Color.BLACK, 5)
	
	if show_circle_world:
		game.draw_circle_world(obj.pos, radius, 30, 3, Color.RED)
	
	if show_circle_map:
		p = game.world_to_minimap(obj.pos)
		#print(f'{obj.name} = {p.x:.2f} {p.y:.2f}')
		game.draw_circle(game.world_to_minimap(obj.pos), game.distance_to_minimap(radius), 15, 2, Color.RED)

def lview_update(game, ui):
	
	global show_clones, show_wards, show_traps
	global traps, wards, clones
	
	for obj in game.others:
		if obj.is_ally_to(game.player):
			continue
		
		if show_wards and obj.has_tags(UnitTag.Unit_Ward) and obj.name in wards:
			draw(game, obj, *(wards[obj.name]))
		elif show_traps and obj.has_tags(UnitTag.Unit_Special_Trap) and obj.name in traps:
			draw(game, obj, *(traps[obj.name]))
		elif show_clones and obj.name in clones:
			draw(game, obj, *(clones[obj.name]))
		