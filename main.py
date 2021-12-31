import shortlister as sh
import scouter as sc

print('Welcome to FM 19 Touch Scouter')
sh.import_shortlists()
shortlist = sc.get_shortlist()
report = sc.scouting_report(shortlist)
sc.view_report(report)