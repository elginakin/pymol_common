# Generated profile: C.5.6.1
# Example C.5.6.1 mutation layer requested by the author.
# Mutation input uses sequential B/Brisbane/60/2008 HA1 numbering.
# This file is generated.  Edit the JSON configs and regenerate it.

reinitialize
set fetch_path, cache
fetch 4fqm, ha_4fqm, type=pdb1, async=0
remove solvent

set_color ha_body, [0.8275, 0.8431, 0.8667]
set_color ha_context, [0.9882, 0.9882, 1.0000]
set_color site_120_blue, [0.6784, 0.8510, 0.9608]
set_color site_150_blue, [0.3882, 0.6784, 0.8784]
set_color site_160_blue, [0.1569, 0.4706, 0.7294]
set_color site_190_blue, [0.0510, 0.2392, 0.4784]
set_color mutation_red, [0.8431, 0.0980, 0.1098]
set_color glycan_gold, [0.9020, 0.6706, 0.0078]
set_color rbs_purple, [0.4784, 0.2902, 0.6863]

select focus_ha1, ha_4fqm and polymer.protein and chain A
select focus_ha2, ha_4fqm and polymer.protein and chain B
select focus_protomer, focus_ha1 or focus_ha2
select context_ha1, ha_4fqm and polymer.protein and chain C+E
select context_ha2, ha_4fqm and polymer.protein and chain D+F
select context_protomers, context_ha1 or context_ha2
select trimer_protein, focus_protomer or context_protomers

select antigenic_120_loop, focus_ha1 and resi 116-137
select antigenic_150_loop, focus_ha1 and resi 141-150
select antigenic_160_loop, focus_ha1 and resi 162-167
select antigenic_190_helix, focus_ha1 and resi 194-202
select antigenic_sites, antigenic_120_loop or antigenic_150_loop or antigenic_160_loop or antigenic_190_helix
select rbs_focus, focus_ha1 and resi 95+140+158+191+202+238+240
select mutation_199, focus_ha1 and resi 196
select mutations_focus, mutation_199

select glycan_HA1_N25, ha_4fqm and resn NAG+BMA and (chain O)
select glycan_HA1_N59, ha_4fqm and resn NAG+BMA and (chain A and resi 411)
select glycan_HA1_N145, ha_4fqm and resn NAG+BMA and (chain M)
select glycan_HA1_N197, ha_4fqm and resn NAG+BMA and (chain Q)
select glycan_HA1_N233, ha_4fqm and resn NAG+BMA and (chain A and resi 415)
select glycan_HA1_N304, ha_4fqm and resn NAG+BMA and (chain N)
select glycan_HA1_N333, ha_4fqm and resn NAG+BMA and (chain P)
select glycan_HA2_N145, ha_4fqm and resn NAG+BMA and (chain B and resi 600)
select focus_glycans, glycan_HA1_N25 or glycan_HA1_N59 or glycan_HA1_N145 or glycan_HA1_N197 or glycan_HA1_N233 or glycan_HA1_N304 or glycan_HA1_N333 or glycan_HA2_N145
select emphasized_glycans, glycan_HA1_N197

hide everything, ha_4fqm
show cartoon, focus_protomer
color ha_body, focus_protomer
show surface, context_protomers
color ha_context, context_protomers
set transparency, 0.62, context_protomers
show spheres, antigenic_sites
color site_120_blue, antigenic_120_loop
color site_150_blue, antigenic_150_loop
color site_160_blue, antigenic_160_loop
color site_190_blue, antigenic_190_helix
set sphere_scale, 0.72, antigenic_sites
show sticks, rbs_focus
show spheres, rbs_focus
color rbs_purple, rbs_focus
set stick_radius, 0.19, rbs_focus
set sphere_scale, 0.8, rbs_focus
show sticks, mutations_focus
show spheres, mutations_focus
color mutation_red, mutations_focus
set sphere_scale, 0.82, mutations_focus
show sticks, focus_glycans
color glycan_gold, focus_glycans
set stick_radius, 0.22, focus_glycans
show spheres, emphasized_glycans
color glycan_gold, emphasized_glycans
set sphere_scale, 0.27, emphasized_glycans

bg_color white
set orthoscopic, on
set depth_cue, off
set fog, 0
set antialias, 2
set ray_opaque_background, off
set ray_trace_mode, 1
set ray_trace_gain, 0.08
set ray_shadows, on
set ambient, 0.48
set direct, 0.42
set specular, 0.18
set shininess, 25
set cartoon_fancy_helices, on
set cartoon_smooth_loops, on
set surface_quality, 1
set stick_quality, 18
set sphere_quality, 2

disable all
enable ha_4fqm
orient trimer_protein
turn z, -90
turn y, 150
zoom trimer_protein, 8
scene overview, store
zoom (focus_ha1 and resi 185-205) or emphasized_glycans, 10
scene glycan_closeup, store
scene overview, recall

viewport 1800, 2400
ray 1800, 2400
png outputs/figures/ha_4fqm_c_5_6_1.png, dpi=300
save outputs/sessions/ha_4fqm_c_5_6_1.pse
scene glycan_closeup, recall
deselect
