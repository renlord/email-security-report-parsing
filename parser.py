import base64
import json
from gzip import decompress

# returns dict of header-[value1,value2] mapping
def parse_header(text):
    stuff = {}
    for line in text:
        if line == '\n':
            break
        _a = line.split(':')
        try:
            header = _a[0].strip(' ')
            value = _a[1].strip('\n ')
            if header not in stuff:
                stuff[header] = [value]
            else:
                stuff[header].append(value)
        except IndexError:
            continue
    return stuff

def extract_attachments(text):
    attachments = []
    attachment_state = None
    # body attachments are composed of (header, content)
    # and the entire attachment follows the format --, \n, \n
    for line in text:
        if line[:2] == '--' and attachment_state == None:
            attachment_text = []
            attachment_body = []
            attachment_state = 'header'

        if attachment_state != 'end' and attachment_state != None:
            attachment_text.append(line.strip('\n'))
            if attachment_state == 'mid':
                attachment_body.append(line.strip('\n'))

        if attachment_state == 'mid' or attachment_state == 'header':
            if line == '\n':
                if attachment_state == 'header':
                    attachment_state = 'mid'
                elif attachment_state == 'mid':
                    attachment_state = 'end'

        if attachment_state == 'end':
            attachment_header = parse_header(attachment_text)
            attachment_body = ''.join(attachment_body)
            attachment = (attachment_header, attachment_body)
            attachments.append(attachment)
            attachment_state = None

    if attachment_state != 'end':
        # google TLS report emails dont have an additional line space to 
        # delimit final attachments
        attachment_header = parse_header(attachment_text)
        attachment_body = attachment_body[:-1]
        attachment_body = ''.join(attachment_body)
        attachment = (attachment_header, attachment_body)
        attachments.append(attachment)
        attachment_state = None

    return attachments

def process_tls_report(attachment):
    return report

def is_tls_report_email(text):
    if 'TLS-Report-Domain' in parse_header(text):
        return True
    else:
        return False

def check_tls_report_header(text):
    # {'Content-Type': ['application/octet-stream;'], 'Content-Description': [''], 'Content-Disposition': ['attachment;'], 'Content-Transfer-Encoding': ['base64']}
    try:
        # microsoft content-type
        return (text['Content-Type'][0] == 'application/octet-stream;' or \
                # google content-type
                text['Content-Type'][0] == 'application/tlsrpt+gzip;') and \
                text['Content-Transfer-Encoding'][0] == 'base64'
    except:
        return False

def gzipbase64_to_text(text, gzip=True, format='json'):
    s = base64.b64decode(text)
    if gzip:
        s = decompress(s).decode('utf-8')
    else: s = s.decode('utf-8')
    return s

def is_dmarc_report_email(text):
    # TODO
    return False

def check_dmarc_report_header(text):
    # TODO
    return False

def short_tls_report(json_text):
    o = json.loads(json_text)
    org = o['organization-name']
    date = o['date-range']['start-datetime']
    success = o['policies'][0]['summary']['total-successful-session-count']
    failure = o['policies'][0]['summary']['total-failure-session-count']
    return f'{date},{org},{success},{failure}'
