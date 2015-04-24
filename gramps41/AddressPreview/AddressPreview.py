from __future__ import unicode_literals

from gi.repository import Gtk

from gramps.gen.plug import Gramplet
from gramps.gui.widgets import Photo
from gramps.gen.const import GRAMPS_LOCALE as glocale

from gramps.gen.utils.place import conv_lat_lon
from gramps.gen.utils.file import media_path_full
from gramps.gen.display.place import displayer as place_displayer
from gi.repository import Gtk
from gi.repository import Pango
from gramps.gen.lib import PlaceType
from gramps.gen.lib import Place
from gramps.gen.utils.location import get_main_location
from gramps.gui.dbguielement import DbGUIElement
from gramps.gen.lib.date import Today

try:
    trans = glocale.get_addon_translator(__file__)
except ValueError:
    trans = glocale.translation
_ = trans.gettext


class AddressPreview(Gramplet, DbGUIElement):
    """
    Displays the participants of an event.
    """
    def __init__(self, gui, nav_group=0):
        Gramplet.__init__(self, gui, nav_group)
        DbGUIElement.__init__(self, self.dbstate.db)

    def _connect_db_signals(self):
        """
        called on init of DbGUIElement, connect to db as required.
        """
        self.callman.register_callbacks({'place-update': self.changed,
                                         'event-update': self.changed})
        self.callman.connect_all(keys=['place', 'event'])
        #self.dbstate.db.connect('person-update', self.update)
        self.connect_signal('Place', self.update)

    def changed(self, handle):
        """
        Called when a registered person is updated.
        """
        self.update()

    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add_with_viewport(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        """
        Build the GUI interface.
        """
        self.top = Gtk.HBox()
        vbox = Gtk.VBox()
        self.photo = Photo(self.uistate.screen_height() < 1000)
        self.title = Gtk.Label()
        self.title.set_alignment(0, 0)
        self.title.modify_font(Pango.FontDescription('sans bold 12'))
        vbox.pack_start(self.title, False, True, 7)
        self.table = Gtk.Table(n_rows=1, n_columns=2)
        vbox.pack_start(self.table, False, True, 0)
        self.top.pack_start(self.photo, False, True, 5)
        self.top.pack_start(vbox, False, True, 10)
        self.top.show_all()
        return self.top

# ------------------------------------------------------------------------------------------

    _address_format = ["street, custom, unknown, building, department, farm, neighborhood",
                       "hamlet, village, borough, locality",
                       "code[ town, city, municipality], parish",
                       "district, region, province, county, state",
                       "country",
                       ""]

    _place_keys = ['street', 'department', 'building', 'farm', 'neighborhood', 'hamlet', 'village',
                  'borough', 'locality', 'town', 'city', 'municipality', 'parish', 'district',
                  'region', 'province', 'county', 'state', 'country', 'custom', 'unknown', 'code']

    _place_types = dict(street=PlaceType.STREET,
                       department=PlaceType.DEPARTMENT,
                       building=PlaceType.BUILDING,
                       farm=PlaceType.FARM,
                       neighborhood=PlaceType.NEIGHBORHOOD,
                       hamlet=PlaceType.HAMLET,
                       village=PlaceType.VILLAGE,
                       borough=PlaceType.BOROUGH,
                       locality=PlaceType.LOCALITY,
                       town=PlaceType.TOWN,
                       city=PlaceType.CITY,
                       municipality=PlaceType.MUNICIPALITY,
                       parish=PlaceType.PARISH,
                       district=PlaceType.DISTRICT,
                       province=PlaceType.PROVINCE,
                       region=PlaceType.REGION,
                       county=PlaceType.COUNTY,
                       state=PlaceType.STATE,
                       country=PlaceType.COUNTRY,
                       custom=PlaceType.CUSTOM,
                       unknown=PlaceType.UNKNOWN)

    def add_row(self, title, value):
        """
        Add a row to the table.
        """
        label = Gtk.Label(label=title + ':')
        label.set_alignment(1, 0)
        label.show()
        value = Gtk.Label(label=value)
        value.set_alignment(0, 0)
        value.show()
        rows = self.table.get_property('n-rows')
        rows += 1
        self.table.resize(rows, 2)
        self.table.attach(label, 0, 1, rows, rows + 1, xoptions=Gtk.AttachOptions.FILL,
                                                       xpadding=10)
        self.table.attach(value, 1, 2, rows, rows + 1)

    def clear_table(self):
        """
        Remove all the rows from the table.
        """
        list(map(self.table.remove, self.table.get_children()))
        self.table.resize(1, 2)

    def db_changed(self):
        self.dbstate.db.connect('place-update', self.update)
        self.connect_signal('Place', self.update)

    def update_has_data(self):
        active_handle = self.get_active('Person')
        if active_handle:
            active_person = self.dbstate.db.get_person_from_handle(active_handle)
            self.set_has_data(active_person is not None)
        else:
            self.set_has_data(False)

    def main(self):
        self.display_empty()
        active_handle = self.get_active('Place')
        if active_handle:
            place = self.dbstate.db.get_place_from_handle(active_handle)
            self.top.hide()
            if place:
                self.display_place(place)
                self.set_has_data(True)
            else:
                self.set_has_data(False)
            self.top.show()
        else:
            self.set_has_data(False)

    def display_place(self, place):
        """
        Display details of the active place.
        """
        self.load_place_image(place)
        title = place_displayer.display(self.dbstate.db, place)
        self.title.set_text(title)
        self.clear_table()

        #parser = FormatStringParser(self._place_keys)
        place_dict = self.generate_place_dictionary(place)
        parser = FormatStringParser(place_dict)

        addr1 = parser.parse(place_dict, self._address_format[0])
        addr2 = parser.parse(place_dict, self._address_format[1])
        city = parser.parse(place_dict, self._address_format[2])
        state = parser.parse(place_dict, self._address_format[3])
        country = parser.parse(place_dict, self._address_format[4])
        code = parser.parse(place_dict, self._address_format[5])

        self.add_row(_("Address 1"), addr1)
        self.add_row(_("Address 2"), addr2)
        self.add_row(_("City"), city)
        self.add_row(_("State"), state)
        self.add_row(_("Country"), country)
        self.add_row(_("Postal Code"), code)
        self.add_row(_("Version"), "0.1")

        #self.add_row(_('Name'), place.get_name())
        #self.add_row(_('Type'), place.get_type())
        #self.display_separator()
        #self.display_alt_names(place)
        #self.display_separator()
        lat, lon = conv_lat_lon(place.get_latitude(),
                                place.get_longitude(),
                                format='DEG')
        #if lat:
        #    self.add_row(_('Latitude'), lat)
        #if lon:
        #    self.add_row(_('Longitude'), lon)

    def generate_place_dictionary(self, place):
        db = self.dbstate.get_database()
        location = get_main_location(db, place)
        place_dict = dict()

        for key in self._place_keys:
            place_type = self._place_types.get(key.lower())
            if place_type:
                value = location.get(place_type)
            elif key == "code":
                value = place.get_code()
            else:
                value = ""
            if not value: value = ""

            place_dict[key] = value
        return place_dict


    def display_alt_names(self, place):
        """
        Display alternative names for the place.
        """
        alt_names = place .get_alternative_names()
        if len(alt_names) > 0:
            self.add_row(_('Alternative Names'), '\n'.join(alt_names))

    def display_empty(self):
        """
        Display empty details when no repository is selected.
        """
        self.photo.set_image(None)
        self.photo.set_uistate(None, None)
        self.title.set_text('')
        self.clear_table()

    def display_separator(self):
        """
        Display an empty row to separate groupd of entries.
        """
        label = Gtk.Label(label='')
        label.modify_font(Pango.FontDescription('sans 4'))
        label.show()
        rows = self.table.get_property('n-rows')
        rows += 1
        self.table.resize(rows, 2)
        self.table.attach(label, 0, 1, rows, rows + 1, xoptions=Gtk.AttachOptions.FILL)

    def load_place_image(self, place):
        """
        Load the primary image if it exists.
        """
        media_list = place.get_media_list()
        if media_list:
            media_ref = media_list[0]
            object_handle = media_ref.get_reference_handle()
            obj = self.dbstate.db.get_object_from_handle(object_handle)
            full_path = media_path_full(self.dbstate.db, obj.get_path())
            mime_type = obj.get_mime_type()
            if mime_type and mime_type.startswith("image"):
                self.photo.set_image(full_path, mime_type,
                                     media_ref.get_rectangle())
                self.photo.set_uistate(self.uistate, object_handle)
            else:
                self.photo.set_image(None)
                self.photo.set_uistate(None, None)
        else:
            self.photo.set_image(None)
            self.photo.set_uistate(None, None)

#!/usr/bin/python
#
# FORMAT STRING PARSER
# v0.1
#
# Parses format string with key coded values in dictionary removing unnecessary separators between parsed names
#
# (C) 2015  Kati Haapamaki
#
# ToDo:
# escape char handling
# methods to change default encloser chars
# | option

class ElementType():
    KEY = 1
    SEPARATOR = 2
    PREFIX = 3
    SUFFIX = 4
    PARSED = 0
    PLAINTEXT = 5


class ParseMode():
    ALWAYS = 0
    IFANY = 1
    IFALL = 2


class FormatStringParser():

    _all_keys = []
    _ec_any_start = '['
    _ec_any_end = ']'
    _ec_all_start = '<'
    _ec_all_end = '>'
    _ec_always_start = '{'
    _ec_always_end = '}'
    _escape = '\\'

    def __init__(self, key_list):
        self._all_keys = []
        if type(key_list) is list:
            self._all_keys = key_list
        elif type(key_list) is dict:
            for key, value in key_list.items():
                self._all_keys.append(key)
        else:
            raise TypeError("Incorrect key list type")

    def parse(self, values, format_string):
        parsed_list = self._parse_full_format_string(values, format_string)
        print(parsed_list)
        return self._make_string_from_list(parsed_list)

    def _parse_full_format_string(self, values, format_string, mode=ParseMode.IFANY):
        """
        Recurses format string's enclosed parts, and parses them into tuple list.
        Returns tuple list of elements of partial format string when going thru recursion
        Finally returns tuple list that is suppressed to single item including the full parsed string

        :param values:
        :param format_string:
        :param mode:
        :return:
        """
        encloser_start = self._find_encloser_start(format_string)
        if encloser_start:
            start_pos = encloser_start[0]

            if start_pos >= 0:
                encloser_end = self._find_encloser_end(format_string, encloser_start)
                if encloser_end:
                    end_pos = encloser_end[0]
                    enclosed_mode = encloser_end[1]
                    before = middle = after = ""
                    if end_pos - start_pos >= 2:
                        middle = format_string[start_pos + 1:end_pos]
                    if start_pos > 0:
                        before = format_string[:start_pos]
                    if end_pos < len(format_string) - 1:
                        after = format_string[end_pos + 1:]

                    recursion = self._collect(
                        self._parse_full_format_string(values, before, mode)
                        + self._collect(self._parse_full_format_string(values, middle, enclosed_mode), enclosed_mode)
                        + self._parse_full_format_string(values, after, mode))

                    return recursion

        new_tuple_list = self._collect(self._parse_format_into_list(values, format_string))

        return new_tuple_list


    def _split_format_string_into_tuple_list(self, format_string, separator_mode=False):
        """
        :param format_string:
        :return:
        """

        tuple_list = []
        remainder = format_string
        any_key_found = False
        if remainder:
            while remainder:
                next_key = self._get_next_key(remainder)
                if next_key:
                    before, key, after = remainder.partition(next_key)
                    if before:
                        if any_key_found or separator_mode:
                            separator_tuple = (before, ElementType.SEPARATOR)
                        else:
                            separator_tuple = (before, ElementType.PREFIX)
                        tuple_list.append(separator_tuple)

                    key_tuple = (key, ElementType.KEY)
                    tuple_list.append(key_tuple)
                    any_key_found = True
                    remainder = after
                else:
                    if any_key_found and not separator_mode:
                        separator_tuple = (remainder, ElementType.SUFFIX)
                    else:

                        separator_tuple = (remainder, ElementType.PLAINTEXT)
                    tuple_list.append(separator_tuple)
                    remainder = ""

        return tuple_list

    def _get_next_key(self, format_string):
        """
        Searches for the first valid key in a format string, returns the key if found
        If found key formatted in uppercase, return key will be also uppercase

        :param format_string:
        :return:
        """
        any_found = False
        lowest_index = -1
        found_key = ""

        if format_string:
            for key in self._all_keys:
                pos_lc = format_string.find(key, 0)
                if pos_lc >= 0 and (pos_lc < lowest_index or not any_found):
                    lowest_index = pos_lc
                    any_found = True
                    found_key = key
                pos_uc = format_string.find(key.upper(), 0)
                if pos_uc >= 0 and (pos_uc < lowest_index or not any_found):
                    lowest_index = pos_uc
                    any_found = True
                    found_key = key.upper()
        return found_key

    def _parse_keys_in_list(self, values, tuple_list):
        """
        Parses keys in list

        :param values: dictionary
        :param tuple_list: elements of format string
        :return:
        """
        if len(tuple_list) < 1:
            return []
        new_list = []
        index = 0

        for item, item_type in tuple_list:
            if item_type is not ElementType.KEY:
                replacement = (item, item_type)
                new_list.append(replacement)
            if item_type is ElementType.KEY:
                value = values.get(item.lower())

                if not value:
                    value = ""

                if item.isupper():
                    replacement = (value.upper(), ElementType.PARSED)
                else:
                    replacement = (value, ElementType.PARSED)
                new_list.append(replacement)

            index += 1

        return new_list

    def _make_string_from_list(self, tuple_list):
        str_list = []
        for item, mode in tuple_list:
            str_list.append(item)
        return "".join(str_list)

    def _collect(self, tuple_list, mode=ParseMode.IFANY):
        """
        Suppresses a tuple list to length of 1, disregarding empty parsed strings and separators between them

        :param tuple_list:
        :return:
        """
        string_list = []
        index = 0
        any_parsed = False

        tuple_list = self._fix_separators(tuple_list)

        for item, item_type in tuple_list:
            if item_type == ElementType.PARSED:
                any_parsed = True

            if (item_type == ElementType.PARSED or item_type == ElementType.PLAINTEXT) and item:
                string_list.append(item)

                separator1 = None
                separator2 = None
                found_more = False

                if len(tuple_list) > index + 2:
                    if tuple_list[index+1][1] == ElementType.SEPARATOR:
                        separator1 = tuple_list[index + 1]
                    index2 = index + 1
                    for item2, type2 in tuple_list[index+1:]:
                        if (type2 == ElementType.PARSED or type2 == ElementType.PLAINTEXT) and item2:
                            found_more = True
                            if index2 > index + 2 and tuple_list[index2 - 1][1] == ElementType.SEPARATOR:
                                separator2 = tuple_list[index2 - 1]
                            break
                        index2 += 1

                    separator = separator2 if not separator1 else separator1

                    if separator and found_more:
                        string_list.append(separator[0])

            elif item_type == ElementType.SEPARATOR:
                pass

            elif item_type == ElementType.PREFIX or item_type == ElementType.SUFFIX:
                string_list.append(item)

            index += 1

        parsed_items = self._number_of_non_empty_parsed_item(tuple_list)
        empty_items = self._number_of_empty_parsed_item(tuple_list)

        if mode == ParseMode.ALWAYS:
            print(string_list)

        if mode == ParseMode.IFANY and parsed_items > 0 \
                or mode == ParseMode.ALWAYS \
                or mode == ParseMode.IFALL and parsed_items > 0 and empty_items == 0:

            parsed_string = "".join(string_list)
        else:
            parsed_string = ""

        return[(parsed_string, ElementType.PARSED if any_parsed else ElementType.PLAINTEXT)]

    def _fix_separators(self, tuple_list):
        """
        Should be used to convert suffixes and prefixes that orgin from enclosed parts of format string
        into separators. Must be done before collect/suppress. Working ok?

        :param tuple_list:
        :return:
        """
        index = 0
        new_tuple_list = []
        for item, item_type in tuple_list:
            if index > 0 and index < (len(tuple_list) - 1) \
                    and (item_type == ElementType.PREFIX or item_type == ElementType.SUFFIX):
                new_tuple = item, ElementType.SEPARATOR
            else:
                new_tuple = item, item_type
            new_tuple_list.append(new_tuple)
            index += 1
        return new_tuple_list


    def _number_of_empty_parsed_item(self, tuple_list):
        """

        :param tuple_list:
        :return:
        """
        counter = 0
        for item, item_type in tuple_list:
            if item_type == ElementType.PARSED and not item:
                counter += 1
        return counter

    def _number_of_non_empty_parsed_item(self, tuple_list):
        """

        :param tuple_list:
        :return:
        """
        counter = 0
        for item, item_type in tuple_list:
            if item_type == ElementType.PARSED and item:
                counter += 1
        return counter

    def _parse_format_into_list(self, values, format_string):
        """
        Splits format string into tuple list, and then parses keys included in it

        :param values:
        :param format_string:
        :return:
        """
        tuple_list = self._split_format_string_into_tuple_list(format_string)
        parsed_list = self._parse_keys_in_list(values, tuple_list)
        return parsed_list

    def _find_encloser_start(self, format_string, start_pos=0):
        index = start_pos
        found_encloser = None
        for c in format_string[start_pos:]:
            if c == self._ec_any_start:
                found_encloser = index, ParseMode.IFANY
            elif c == self._ec_all_start:
                found_encloser = index, ParseMode.IFALL
            elif c == self._ec_always_start:
                found_encloser = index, ParseMode.ALWAYS
            if found_encloser and index > start_pos:
                if format_string[index-1] == self._escape:
                    found_encloser = None # flush found encloser if it's follower by escape char
                else:
                    break
            index += 1

        return found_encloser

    def _find_encloser_end(self, format_string, encloser_start):
        start_pos = encloser_start[0] + 1
        found_encloser_end = None

        if len(format_string)- start_pos > 1:

            mode = encloser_start[1]
            if mode == ParseMode.IFALL:
                ec_end_char = self._ec_all_end
            elif mode == ParseMode.ALWAYS:
                ec_end_char = self._ec_always_end
            else:
                ec_end_char = self._ec_any_end

            index = start_pos
            level = 0
            for c in format_string[start_pos:]:
                if self._is_encloser_end_char(c):
                    if level == 0 and c == ec_end_char:
                        found_encloser_end = index, mode
                        break
                    else:
                        level -= 1
                        if index > start_pos:
                            if format_string[index-1] == self._escape:
                                level += 1 # was escape, step back
                elif self._is_encloser_start_char(c):
                    level += 1
                    if index > start_pos:
                        if format_string[index-1] == self._escape:
                            level -= 1 # was escape, step back

                index += 1

        return found_encloser_end

    def _is_encloser_start_char(self, c):
        if not c:
            return False
        return c == self._ec_all_start or c == self._ec_any_start or c == self._ec_always_start

    def _is_encloser_end_char(self, c):
        if not c:
            return False
        return c == self._ec_all_end or c == self._ec_any_end or c == self._ec_always_end

    def _is_encloser_char(self, c):
        return self._is_encloser_start_char(c) or self._is_encloser_end_char(c)
