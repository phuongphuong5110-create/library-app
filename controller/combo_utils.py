def fill_combobox_with_ids(combo, id_name_pairs):
    combo.clear()
    for row_id, label in id_name_pairs:
        combo.addItem(label, row_id)


def set_combo_current_data(combo, row_id):
    idx = combo.findData(row_id)
    if idx >= 0:
        combo.setCurrentIndex(idx)
