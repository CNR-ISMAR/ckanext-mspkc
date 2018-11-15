import sys
from ckan.common import _
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import simplejson
from collections import OrderedDict
import routes.mapper
import ckan.lib.base as base


class MspkcPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IRoutes)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'mspkc')

    # IFacets

    def dataset_facets(self, facets_dict, package_type):

        self._update_facets(facets_dict)
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):

        self._update_facets(facets_dict)
        return facets_dict

    def organization_facets(self, facets_dict, organization_type, package_type):

        self._update_facets(facets_dict)
        return facets_dict

    def _update_facets(self, facets_dict):
        # removing some default items
        del facets_dict['tags']
        del facets_dict['organization']
        del facets_dict['groups']
        _facets_items = (
            ('metadata_completeness', plugins.toolkit._('Metadata completeness')),
            ('vocab_owner', plugins.toolkit._('Owner')),
            ('vocab_web_services', plugins.toolkit._('Web services')),
            ('vocab_domain_area', plugins.toolkit._('Domain area')),
            ('vocab_category', plugins.toolkit._('Category')),
            ('dataset_type', plugins.toolkit._('Type')),
        )
        # add new items as firsts
        for item in _facets_items:
            ordered_dict_prepend(facets_dict, item[0], item[1])
        print >> sys.stderr, facets_dict

    def before_index(self, dataset_dict):
        split_terms = ['owner', 'domain_area', 'web_services', 'category']
        for st in split_terms:
            st_value = dataset_dict.get(st, None)
            if st_value is not None:
                vocab_item = 'vocab_{}'.format(st)
                if st_value.startswith('['):
                    # it's a json
                    st_items = simplejson.loads(st_value)
                else:
                    st_items = st_value.split(',')
                print >> sys.stderr, vocab_item
                print >> sys.stderr, st_value
                print >> sys.stderr, st_items
                dataset_dict[vocab_item] = st_items
        return dataset_dict

    def before_map(self, route_map):
        with routes.mapper.SubMapper(route_map,
                                     controller='ckanext.mspkc.plugin:MspkcController') as m:
            m.connect('analysis', '/analysis',
                      action='analysis')
        return route_map

    def after_map(self, route_map):
        return route_map


class MspkcController(base.BaseController):
    def analysis(self):
        c = toolkit.c
        c.test_message = 'tttt'
        return toolkit.render('analysis.html')
        # return base.render(')


# https://stackoverflow.com/questions/16664874/how-can-i-add-an-element-at-the-top-of-an-ordereddict-in-python
def ordered_dict_prepend(dct, key, value, dict_setitem=dict.__setitem__):
    root = dct._OrderedDict__root
    first = root[1]
    if key in dct:
        link = dct._OrderedDict__map[key]
        link_prev, link_next, _ = link
        link_prev[1] = link_next
        link_next[0] = link_prev
        link[0] = root
        link[1] = first
        root[1] = first[0] = link
    else:
        root[1] = first[0] = dct._OrderedDict__map[key] = [root, first, key]
        dict_setitem(dct, key, value)
