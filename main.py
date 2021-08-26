import src.shortlister as sh
import src.scouter as sc

sh.import_shortlists()
shortlist = sc.get_shortlist()
report = sc.scouting_report(shortlist)
sc.view_report(report)