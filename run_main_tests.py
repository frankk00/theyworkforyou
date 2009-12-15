#!/usr/bin/python2.5

from common import *
from testing import *
from subprocess import call, check_call, Popen
import time
import re
import sys
from optparse import OptionParser
from BeautifulSoup import BeautifulSoup
from browser import *
import cgi

def run_main_tests(output_directory):
    check_dependencies()
    setup_configuration()

    start_all_coverage = uml_date()

    # Fetch the main page:

    main_page_test = run_http_test(output_directory,
                                   "/",
                                   test_name="Fetching main page",
                                   test_short_name="basic-main-page")

    def recent_event(http_test,header,item):
        # We want to check that the list on the front page has links
        # to the recent debates.  First fine a matching <h4>
        soup = http_test.soup
        h = soup.find( lambda x: x.name == 'h4' and tag_text_is(x,header) )
        if not h:
            return False
        ul = next_tag(h)
        if not (ul.name == 'ul'):
            return False
        for li in ul.contents:
            if not (li and li.name == 'li'):
                continue
            if tag_text_is(li,item):
                return True
        return False

    items_to_find = [ ("The most recent Commons debates", "Business Before Questions"),
                      ("The most recent Lords debates", "Africa: Water Shortages &#8212; Question"),
                      ("The most recent Westminster Hall debates", "[Sir Nicholas Winterton in the Chair] &#8212; Oil and Gas"),
                      ("The most recent Written Answers","Work and Pensions"),
                      ("The most recent Written Ministerial Statements", "House of LordsEU: Justice and Home Affairs CouncilGlobal Entrepreneurship WeekLondon Underground") ]

    i = 0
    for duple in items_to_find:
        run_page_test(output_directory,
                      main_page_test,
                      lambda t: recent_event(t,duple[0],duple[1]),
                      test_name="Checking that '"+duple[0]+"' contains '"+duple[1]+"'",
                      test_short_name="main-page-recent-item-"+str(i))
        i += 1

    # ------------------------------------------------------------------------

    def busiest_debate(http_test,header,text):
        soup = http_test.soup
        h = soup.find( lambda x: (x.name == 'h3' or x.name == 'h4') and tag_text_is(x,header) )
        if not h:
            print "Failed to find header with text '"+header+"'"
            return False
        ns = next_tag(next_tag(h,sibling=False),sibling=False)
        print "Next tag is:"
        print ns.prettify()
        return tag_text_is(ns,text)

    main_scotland_page_test = run_http_test(output_directory,
                                            "/scotland/",
                                            test_name="Fetching main page for Scotland",
                                            test_short_name="basic-main-scotland-page")

    header = "Busiest Scottish Parliament debates from the most recent week"
    text = 'Scottish Economy (103 speeches)'

    run_page_test(output_directory,
                  main_scotland_page_test,
                  lambda t: busiest_debate(t,header,text),
                  test_name="Checking that first item in '"+header+"' is '"+text+"'",
                  test_short_name="main-scotland-page-busiest-0")

    def any_answer(http_test,header):
        soup = http_test.soup
        h = soup.find( lambda x: x.name == 'h3' and tag_text_is(x,header) )
        if not h:
            print "Failed to find header with text '"+header+"'"
            return False
        ns = next_tag(next_tag(h,sibling=False),sibling=False)
        stringified = non_tag_data_in(ns)
        return re.search('\(2[0-9]\s+October\s+2009\)',stringified)

    header = "Some recent written answers"

    run_page_test(output_directory,
                  main_scotland_page_test,
                  lambda t: any_answer(t,header),
                  test_name="Checking that there's some random answer under '"+header+"'",
                  test_short_name="main-scotland-page-any-written")

    # ------------------------------------------------------------------------

    main_ni_page_test = run_http_test(output_directory,
                                            "/ni/",
                                            test_name="Fetching main page for Northern Ireland",
                                            test_short_name="basic-main-ni-page")

    header = "Busiest debates from the most recent month"
    text = u"Private Members&#8217; Business"

    run_page_test(output_directory,
                  main_ni_page_test,
                  lambda t: busiest_debate(t,header,text),
                  test_name="Checking that first item in '"+header+"' is '"+text+"'",
                  test_short_name="main-ni-page-busiest-0")

    # ------------------------------------------------------------------------

    main_wales_page_test = run_http_test(output_directory,
                                            "/wales/",
                                            test_name="Fetching main page for wales",
                                            test_short_name="basic-main-wales-page")

    run_page_test(output_directory,
                  main_wales_page_test,
                  lambda t: t.soup.find( lambda x: x.name == 'h3' and tag_text_is(x,"We need you!") ),
                  test_name="Checking that the Wales page still asks for help",
                  test_short_name="main-wales-page-undone")

    # ------------------------------------------------------------------------

    mps_test = run_http_test(output_directory,
                             "/mps/",
                             test_name="Fetching basic MPs page",
                             test_short_name="basic-MPs",
                             render=False) # render fails on a page this size...

    # This uses the result of the previous test to check that Diane
    # Abbot (the first MP in this data set) is in the list.

    run_page_test(output_directory,
                  mps_test,
                  lambda t: 1 == len(t.soup.findAll( lambda tag: tag.name == "a" and tag.string and tag.string == "Diane Abbott" )),
                  test_name="Diane Abbott in MPs page",
                  test_short_name="mps-contains-diane-abbott")

    # As a slightly different example of doing the same thing, define
    # a function instead of using nested lambdas:

    def link_from_mp_name(http_test,name):
        all_tags = http_test.soup.findAll( lambda tag: tag.name == "a" and tag.string and tag.string == name)
        return 1 == len(all_tags)

    run_page_test(output_directory,
                  mps_test,
                  lambda t: link_from_mp_name(t,"Richard Younger-Ross"),
                  test_name="Richard Younger-Ross in MPs page",
                  test_short_name="mps-contains-richard-younger-ross")

    # ------------------------------------------------------------------------

    msps_test = run_http_test(output_directory,
                              "/msps/",
                              test_name="Fetching basic MSPs page",
                              test_short_name="basic-MSPs")

    run_page_test(output_directory,
                  msps_test,
                  lambda t: link_from_mp_name(t,"Brian Adam"),
                  test_name="Brian Adam in MSPs page",
                  test_short_name="msps-contains-brian-adam")

    run_page_test(output_directory,
                  msps_test,
                  lambda t: link_from_mp_name(t,"John Wilson"),
                  test_name="John Wilson in MSPs page",
                  test_short_name="msps-contains-john-wilson")

    # ------------------------------------------------------------------------

    mlas_test = run_http_test(output_directory,
                              "/mlas/",
                              test_name="Fetching basic MLAs page",
                              test_short_name="basic-MLAs")

    run_page_test(output_directory,
                  mlas_test,
                  lambda t: link_from_mp_name(t,"Gerry Adams"),
                  test_name="Gerry Adams in MLAs page",
                  test_short_name="msps-contains-gerry-adams")

    run_page_test(output_directory,
                  mlas_test,
                  lambda t: link_from_mp_name(t,"Sammy Wilson"),
                  test_name="Sammy Wilson in MLAs page",
                  test_short_name="msps-contains-sammy-wilson")

    # ------------------------------------------------------------------------

    # Check a written answer from Scotland:

    spwrans_test = run_http_test(output_directory,
                                 "/spwrans/?id=2009-10-26.S3W-27797.h",
                                 test_name="Testing Scottish written answer",
                                 test_short_name="spwrans",
                                 append_id=False)

    def check_speaker_and_speech_tag(expected_name, got_name, expected_speech, got_speech_tag):
        if not expected_name == got_name:
            print "Speaker name didn't match:"
            print "Expected '"+expected_name+"', but got '"+got_name+"'"
            return False
        if not tag_text_is(got_speech_tag,expected_speech):
            print "Text didn't match..."
            return False
        return True

    def check_written_answer(t,q_name,q_text,a_name,a_text):
        labour_speakers = t.soup.findAll(attrs={'class':'speaker labour'})
        snp_speakers = t.soup.findAll(attrs={'class':'speaker scottish national party'})
        if not 1 == len(labour_speakers):
            print "Couldn't find the unique question, should be from a Labour speaker"
            return False
        speaker = labour_speakers[0]
        speaker_name = speaker.contents[0].contents[0].string
        question_tag = next_tag(speaker)
        if not check_speaker_and_speech_tag(q_name,speaker_name,q_text,question_tag):
            return False
        speaker = snp_speakers[0]
        speaker_name = speaker.contents[0].contents[0].string
        question_tag = next_tag(speaker)
        if not check_speaker_and_speech_tag(a_name,speaker_name,a_text,question_tag):
            return False
        return True

    run_page_test(output_directory,
                  spwrans_test,
                  lambda t: check_written_answer(t,
                                                 "Sarah Boyack",
                                                 "To ask the Scottish Executive how many properties it has disposed of in the last two years to which section 68 of the Climate Change (Scotland) Act 2009 could have been applied.",
                                                 "John Swinney",
                                                 "No core Scottish Government-owned buildings, to which section 68 of the Climate Change (Scotland) Act 2009 could have been applied, have been sold by the Scottish Government in the last two years."),
                  test_name="Checking text of Scottish Written Answer",
                  test_short_name="spwrans-content")





    # ------------------------------------------------------------------------

    # Find a representative based on postcode:

    postcode_test = run_http_test(output_directory,
                                  "/postcode/?pc=EH8+9NB",
                                  test_name="Testing postcode lookup",
                                  test_short_name="postcode",
                                  append_id=False)

    run_page_test(output_directory,
                  postcode_test,
                  lambda t: t.soup.find( lambda x: x.name == 'h2' and x.string and x.string == "Denis Murphy" ),
                  test_name="Looking for valid postcode result",
                  test_short_name="postcode-result")

    # ------------------------------------------------------------------------

    run_http_test(output_directory,
                  "/mp/gordon_brown/kirkcaldy_and_cowdenbeath",
                  test_name="Fetching Gordon Brown's page",
                  test_short_name="gordon-brown")

    end_all_coverage = uml_date()

    # ========================================================================
    # Generate the coverage report:

    output_filename_all_coverage = os.path.join(output_directory,"coverage")

    coverage_data = coverage_data_between(start_all_coverage,end_all_coverage)
    fp = open(output_filename_all_coverage,"w")
    fp.write(coverage_data)
    fp.close()

    used_source_directory = os.path.join(output_directory,"mysociety")

    check_call(["mkdir","-p",used_source_directory])

    rsync_from_guest("/data/vhost/theyworkforyou.sandbox/mysociety/twfy/",
                     os.path.join(used_source_directory,"twfy"),
                     user="alice",
                     verbose=False)

    rsync_from_guest("/data/vhost/theyworkforyou.sandbox/mysociety/phplib/",
                     os.path.join(used_source_directory,"phplib"),
                     user="alice",
                     verbose=False)

    report_index_filename = os.path.join(output_directory,"report.html")
    fp = open(report_index_filename,"w")

    # Generate complete coverage report:
    coverage_report_leafname = "coverage-report"
    generate_coverage("/data/vhost/theyworkforyou.sandbox/mysociety/",
                      output_filename_all_coverage,
                      os.path.join(output_directory,coverage_report_leafname),
                      used_source_directory)

    fp.write('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<head>
<title>They Work For You Test Reports</title>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<style type="text/css">
%s
</style>
</head>
<body style="background-color: #ffffff">
<h2>They Work For You Test Reports</h2>
<p><a href="%s/coverage.html">Code coverage report for all tests.</a>
</p>
''' % (standard_css(),coverage_report_leafname))

    for t in all_tests:
        print "=============="
        print str(t)

        passed_colour = "#96ff81"
        failed_colour = "#ff8181"

        if t.succeeded():
            background_colour = passed_colour
        else:
            background_colour = failed_colour

        fp.write("<div class=\"test\" style=\"background-color: %s\">\n"%(background_colour,))
        fp.write("<h3>%s</h3>\n" % (t.test_name.encode('UTF-8'),))
        fp.write("<h4>%s</h4>\n" % (t.get_id_and_short_name(),))
        fp.write("<pre>\n")
        fp.write(cgi.escape(file_to_string(os.path.join(t.test_output_directory,"info"))))
        fp.write("</pre>\n")
        if t.test_type == TEST_HTTP:
            # Generate coverage information:
            coverage_data_file = os.path.join(t.test_output_directory,"coverage")
            coverage_report_directory = os.path.join(t.test_output_directory,coverage_report_leafname)
            print "Using parameters:"
            print "coverage_data_file: "+coverage_data_file
            print "coverage_report_directory: "+coverage_report_directory
            print "used_source_directory: "+used_source_directory
            print "t.test_output_directory is: "+t.test_output_directory
            generate_coverage("/data/vhost/theyworkforyou.sandbox/mysociety/",
                              coverage_data_file,
                              coverage_report_directory,
                              used_source_directory)
            relative_url = os.path.join(os.path.join(t.get_id_and_short_name(),coverage_report_leafname),"coverage.html")
            fp.write("<p><a href=\"%s\">Code coverage for this test.</a></p>\n" % (relative_url,))
            if t.render and t.full_image_filename:
                # fp.write("<div style=\"float: right\">")
                fp.write("<div>")
                relative_full_image_filename = re.sub(re.escape(output_directory),'',t.full_image_filename)
                relative_thumbnail_image_filename = re.sub(re.escape(output_directory),'',t.thumbnail_image_filename)
                fp.write("<a href=\"%s\"><img src=\"%s\"></a>" % (relative_full_image_filename,relative_thumbnail_image_filename))
                fp.write("</div>")
        elif t.test_type == TEST_SSH:
            for s in ("stdout","stderr"):
                fp.write("<h4>%s</h4>" % (s,))
                fp.write("<div class=\"stdout_stderr\"><pre>")
                fp.write(cgi.escape(file_to_string(os.path.join(t.test_output_directory,s))))
                fp.write("</pre></div>")
        fp.write("</div>\n")

    fp.write('''</table>
</body>
</html>''')
    fp.close()

if __name__ == '__main__':
    parser = OptionParser(usage="Usage: %prog [OPTIONS]")
    parser.add_option('-o', '--output-directory', dest="output_directory",
                      help="override the default test output directory (./output/[TIMESTAMP]/)")
    options,args = parser.parse_args()
    if options.output_directory:
        output_directory = options.output_directory
    else:
        output_directory = create_output_directory() 

    check_call(["mkdir","-p",output_directory])

    run_main_tests(output_directory)
