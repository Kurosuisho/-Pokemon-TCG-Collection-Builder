# -Pokemon-TCG-Collection-Builder

To-Do:


fix get all cards bug:
"error": "(psycopg2.errors.InvalidTextRepresentation) FEHLER:  ungültige Eingabesyntax für Typ integer: »hgss4-1«\nLINE 3: WHERE cards.id = 'hgss4-1'\n                         ^\n\n[SQL: SELECT cards.id AS cards_id, cards.name AS cards_name, cards.set_name AS cards_set_name, cards.card_type AS cards_card_type, cards.rarity AS cards_rarity, cards.energy_type AS cards_energy_type, cards.hp AS cards_hp, cards.attack_names AS cards_attack_names, cards.description AS cards_description, cards.evolution_stage AS cards_evolution_stage, cards.weakness AS cards_weakness, cards.resistance AS cards_resistance, cards.retreat_cost AS cards_retreat_cost, cards.created_at AS cards_created_at \nFROM cards \nWHERE cards.id = %(pk_1)s]\n[parameters: {'pk_1': 'hgss4-1'}]\n(Background on this error at: https://sqlalche.me/e/20/9h9h)"

add collection to user

add deck to user

add card to collection

add card from specific collection to deck