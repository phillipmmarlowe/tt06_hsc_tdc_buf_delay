prefix_str="tt_export_*"
target_cells = ['sky130_fd_sc_hd__and2_1', 'sky130_fd_sc_hd__fa_1', 'sky130_fd_sc_hd__edfxtp_1']
target_cells.each do |targ_cell|
	prune_cells = []
	layout = RBA::Layout::new
	layout.read($input)
	layout.each_cell do |cell|
		cell_name = layout.cell_name(cell.cell_index)
		if targ_cell == cell_name
			puts "Found " + cell_name
			new_cell_name = prefix_str.gsub(/#/, cell.cell_index.to_s).gsub(/\*/, cell_name)
			layout.rename_cell(cell.cell_index, new_cell_name)
		else
			puts "Other cell " + cell_name
			prune_cells = prune_cells + [cell_name]
		end
	end
	prune_cells.each do |cell|
		puts "Pruning " + cell
		layout.prune_cell(layout.cell_by_name(cell), -1)
	end
	new_cell_name = prefix_str.gsub(/\*/, "") + targ_cell
	layout.write($output_dir + new_cell_name + ".gds")
end