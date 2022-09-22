from model_bakery.recipe import Recipe, seq, foreign_key
from todos_los_nodos import models

test_site = Recipe(
    models.Site,
)

test_switch = Recipe(
    models.Switch,
    name=seq('00', suffix='A'),
    tipo='GI',
    poe=True,
    site=foreign_key(test_site),
)

test_nodo = Recipe(
    models.Nodo,
    nombre=seq("00A-0-0"),
    port=seq("0/"),
    switch=foreign_key(test_switch)
)
