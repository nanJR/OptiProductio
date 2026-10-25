import re, json, sys
md = open(sys.argv[1]).read()
sec = md.split('## Glossary: the words this report uses')[1].split('\n---')[0]
rows = [l for l in sec.splitlines() if l.startswith('| **')]
pats = {
 'IIoT': r'\bIIoT\b|industrial internet of things', 'OEE': r'\bOEE\b',
 'Availability': r'(?i)\bavailability\b', 'Performance': r'(?i)\bperformance\b', 'Quality': r'(?i)\bquality\b',
 'OEE proxy': r'OEE proxy', 'Six big losses': r'(?i)six big losses',
 'WIP': r'\bWIP\b|(?i:work[- ]in[- ]process)', 'Throughput': r'(?i)throughput',
 'Cycle time / flow time': r'(?i)cycle time|flow time', "Little's law": r"(?i)little['’]s law",
 'CONWIP': r'CONWIP', 'Kanban': r'(?i)kanban', 'Bottleneck': r'(?i)bottleneck',
 'Active-period method': r'(?i)active[- ]period', 'Takt time': r'(?i)\btakt', 'Pareto chart': r'Pareto',
 'SPC / control chart': r'\bSPC\b|(?i:control chart)', 'MTBF / MTTR': r'MTBF|MTTR', 'PLC': r'\bPLCs?\b',
 'SCADA / HMI': r'SCADA|\bHMI\b', 'Historian': r'(?i)historian', 'Store and forward': r'(?i)store[- ]and[- ]forward',
 'Edge computing': r'(?i)\bedge\b', 'MES': r'\bMES\b', 'MOM': r'\bMOM\b', 'ERP': r'\bERP\b', 'APS': r'\bAPS\b',
 'ISA-95': r'ISA-95', 'ISO 22400': r'ISO 22400', 'Message broker / MQTT': r'MQTT|(?i:\bbroker)',
 'Unified Namespace (UNS)': r'Unified Namespace|\bUNS\b', 'Digital twin': r'(?i)digital twin',
 'Digital thread': r'(?i)digital thread', 'Discrete-event simulation (DES)': r'(?i:discrete[- ]event simulation)|\bDES\b',
 'Knowledge graph': r'(?i)knowledge graph',
}
needs_oee = {'Availability','Performance','Quality'}
out=[]
for r in rows:
    c=[x.strip() for x in r.strip('|').split('|')]
    m=re.match(r'\*\*(.+?)\*\*\s*(.*)',c[0]); key=m.group(1); extra=m.group(2)
    assert key in pats, key
    out.append(dict(term=key, extra=extra, eli5=c[1], analogy=c[2], pat=pats[key], needOEE=key in needs_oee))
# validate regexes in python flavor; JS needs inline flags converted
json.dump(out, open('gloss.json','w'), ensure_ascii=False, indent=0)
print(len(out))
