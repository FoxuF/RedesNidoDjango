from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import ProtectedError
from django.test import TestCase
from model_bakery import baker

from todos_los_nodos import models


class SwitchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # data for whole TestCase
        cls.site = baker.make_recipe('todos_los_nodos.test_site')

    def test_add_good_switch(self):
        new_switch = models.Switch(
            name="00A",
            tipo="GI",
            ip="127.0.0.0",
            poe=True,
            site=self.site,
        )
        new_switch.full_clean()
        new_switch.save()

    def test_add_ipless_switch(self):
        new_switch = models.Switch(
            name="00A",
            tipo="GI",
            poe=True,
            site=self.site,
        )
        self.assertRaises(ValidationError, new_switch.full_clean)
        new_switch.save()

    def test_try_site_delete(self):
        new_switch = models.Switch(
            name="00A",
            tipo="GI",
            ip="127.0.0.0",
            poe=True,
            site=self.site,
        )
        new_switch.full_clean()
        new_switch.save()
        self.assertRaises(ProtectedError, self.site.delete)


class NodosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # data for the whole TestCase
        cls.switch = baker.make_recipe('todos_los_nodos.test_switch')

    def test_good_node(self):
        new_node = models.Nodo(
            nombre="00A-00-01",
            port="0/1",
            switch=self.switch
        )
        new_node.full_clean()
        new_node.save()

    def test_unusual_node(self):
        new_node = models.Nodo(
            nombre="00A-00-01",
            port="10/10",
            switch=self.switch,
        )
        new_node.full_clean()
        new_node.save()

    def test_orphan_node(self):
        orphan_node = models.Nodo(
            nombre="00A-00-01",
        )
        orphan_node.full_clean()
        orphan_node.save()

    def test_node_xnor_constraint(self):
        new_node = models.Nodo(
            nombre="00A-00-01",
            port="0/1"
        )
        new_node.full_clean()
        self.assertRaises(IntegrityError, new_node.save)

    def test_node_invalid_port(self):
        new_node = models.Nodo(
            nombre="00A-00-01",
            port="Gi 1/0",
            switch=self.switch,
        )
        self.assertRaises(ValidationError, new_node.full_clean)

    def test_duplicated_node(self):
        new_node = models.Nodo(
            nombre="00A-00-01",
            port="0/1",
            switch=self.switch,
        )
        new_node.full_clean()
        new_node.save()

        # Create duplicate
        new_node.pk = None
        self.assertRaises(ValidationError, new_node.full_clean)

    def test_same_port_diff_switch(self):
        # cls.switch = baker.make_recipe('todos_los_nodos.test_switch')
        other_switch = baker.make_recipe('todos_los_nodos.test_switch')
        node_1 = models.Nodo(
            nombre="00A-00-01",
            port="0/1",
            switch=self.switch,
        )
        node_1.full_clean()
        node_1.save()
        node_2 = models.Nodo(
            nombre="01A-00-01",
            port="0/1",
            switch=other_switch,
        )
        node_2.full_clean()
        node_2.save()


class EquipoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nodo = baker.make_recipe('todos_los_nodos.test_nodo')

    def test_add_AP_to_node(self):
        new_ap = models.AP(
            name="AP-001",
            ip="127.0.0.1",
            nodo=self.nodo
        )
        new_ap.full_clean()
        new_ap.save()

    def test_add_double_AP_to_same_node(self):
        ap_1 = models.AP(
            name="AP-001",
            ip="127.0.0.1",
            nodo=self.nodo
        )
        ap_1.full_clean()
        ap_1.save()

        ap_2 = models.AP(
            name="AP-002",
            ip="127.0.0.2",
            nodo=self.nodo
        )
        self.assertRaises(ValidationError, ap_2.full_clean)

    def test_add_orphan_tel(self):
        new_tel = models.Telefono(
            modelo="9611",
            serie="13N513001225",
            mac="3475C7EAEEE8",
        )
        new_tel.full_clean()
        new_tel.save()

    def test_add_orphan_pc(self):
        new_pc = models.Equipo(
            tipo="PC",
            name="PC-001",
            mac="3475C7EAEEE8",
        )
        new_pc.full_clean()
        new_pc.save()

    def test_add_pc_and_tel_to_node(self):
        new_tel = models.Telefono(
            modelo="9611",
            serie="13N515508225",
            mac="8483717FA07E",
            nodo=self.nodo,
        )
        new_tel.full_clean()
        new_tel.save()

        new_pc = models.Equipo(
            tipo="PC",
            name="PC-001",
            mac="3475C7EAEEE8",
            ip="127.0.0.1",
            nodo=self.nodo
        )
        new_pc.full_clean()
        new_pc.save()


class UserTests(TestCase):
    def test_create_user(self):
        new_user = models.Usuario(
            nombre="Myriam",
            apellidos="Zuniga",
            login="mzuniga",
        )
        new_user.full_clean()
        new_user.save()

    def test_add_tel_to_user(self):
        node = baker.make_recipe('todos_los_nodos.test_nodo',
                                 nombre='25D-05-35')
        new_user = models.Usuario(
            nombre="Myriam",
            apellidos="Zuniga",
            login="mzuniga",
            ext="5547"
        )
        new_user.full_clean()
        new_user.save()

        new_tel = models.Telefono(
            modelo="9641",
            serie="13N514009652",
            mac="3475c7e9a169",
            nodo=node,
            usuario=new_user,
        )
        new_tel.full_clean()
        new_tel.save()
