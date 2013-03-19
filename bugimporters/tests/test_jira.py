import datetime
import os

import bugimporters.jira
from bugimporters.tests import ObjectFromDict
import bugimporters.tests
import bugimporters.main
import autoresponse

HERE = os.path.dirname(os.path.abspath(__file__))

class TestJiraBugImporter(object):
    @staticmethod
    def assertEqual(x, y):
        assert x == y

    def setup_class(cls):
        # Set up the JiraTrackerModel that will be used here.
        cls.tm = ObjectFromDict(dict(
                tracker_name='JRUBY',
                base_url='http://jira.codehaus.org/browse/JRUBY',
                closed_status='Closed',
                bitesized_field='Component',
                bitesized_text='Intro',
                documentation_field='Component',
                documentation_text='Documentation',
                as_appears_in_distribution='',
                bugimporter='jira.JiraBugImporter',
                queries = ['http://jira.codehaus.org/issues/?jql=project%20%3D%20JRUBY'],
                ))
        cls.im = bugimporters.jira.JiraBugImporter(
            cls.tm,
            bugimporters.tests.ReactorManager(),
            data_transits=None)

    def test_process_existing_bug_urls(self):
        # Reset test state
        self.setup_class()

        # Remove 'queries', and add a bug to existing_bug_urls
        self.tm.queries = []
        self.tm.existing_bug_urls = [
            'http://mercurial.selenic.com/bts/issue1550',
            ]

        # Create the bug spider
        spider = bugimporters.main.BugImportSpider()
        spider.input_data = [self.tm.__dict__]

        # Configure URL<->filename mapping for offline crawling
        url2filename = {
            'http://mercurial.selenic.com/bts/issue1550':
                os.path.join(HERE, 'sample-data', 'closed-mercurial-bug.html'),
            }

        ar = autoresponse.Autoresponder(url2filename=url2filename,
                                        url2errors={})
        items = ar.respond_recursively(spider.start_requests())
        assert len(items) == 1
        assert items[0]['canonical_bug_link'] == url2filename.keys()[0]

    def test_top_to_bottom(self):
        self.setup_class()
        spider = bugimporters.main.BugImportSpider()
        spider.input_data = [self.tm.__dict__]
        url2filename = {'http://mercurial.selenic.com/bts/issue?@action=export_csv&@columns=id,activity,title,creator,status&@sort=-activity&@group=priority&@filter=status,assignedto&@pagesize=50&@startwith=0&status=-1,1,2,3,4,5,6,7,9,10':
                            os.path.join(HERE, 'sample-data', 'fake-mercurial-csv.csv'),
                        'http://mercurial.selenic.com/bts/issue1550':
                            os.path.join(HERE, 'sample-data', 'closed-mercurial-bug.html'),
                        }
        ar = autoresponse.Autoresponder(url2filename=url2filename,
                                        url2errors={})
        items = ar.respond_recursively(spider.start_requests())
        assert len(items) == 1
        item = items[0]
        assert item['canonical_bug_link'] == (
            'http://mercurial.selenic.com/bts/issue1550')

