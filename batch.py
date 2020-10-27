import os, json, datetime
from parser import *

lines = []

for fp in os.listdir('./tls-report-emails'):
    with open(f'tls-report-emails/{fp}', 'r') as fpp:
        text = fpp.readlines()
        if is_tls_report_email(text):
            attachments = extract_attachments(text)
            (tls_report_header, tls_report_binary) = attachments[1]
            if check_tls_report_header(tls_report_header):
                lines.append(short_tls_report(gzipbase64_to_text(tls_report_binary)))

print('\n'.join(sorted(lines, key=lambda x: x.split(',')[0])))
