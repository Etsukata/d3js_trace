#!/usr/bin/python

import sys
import re

stack_traces = []
stack_trace = []
stack_samples = []

def stack_sample_to_dict(sample):

    ret = {}

    if len(sample['stack_trace']) == 1:
        ret['name'] = sample['stack_trace'][0]
        ret['size'] = sample['count']
        return ret

    ret['name'] = sample['stack_trace'][0]
    tail_stack = sample['stack_trace'][1:]
    ret['children'] = [stack_sample_to_dict({
                           'stack_trace' : tail_stack,
                           'count' : sample['count']
                       })]
    return ret

def add_root(d):

    ret = {
        'name' : 'All',
        'children' : [d]
    }
    return ret

def merge_dict(d1, d2):

    def has_same_child(d1, d2):
        for d in d1['children']:
            if d['name'] == d2['children'][0]['name']:
                return True
        return False

    if not d1['name'] == d2['name']:
        print 'error on merge_dict(): root is not same.'
        print 'd1:'
        pprint(d1)
        print 'd2:'
        pprint(d2)
        sys.exit(1)

    if not d1.has_key('children'):
        return merge_dict(d2, d1)

    ret = d1.copy()

    if d2.has_key('children'):
        if has_same_child(ret, d2):
            children = ret['children']
            for i in range(0, len(children)):
                if children[i]['name'] == d2['children'][0]['name']:
                    children[i] = merge_dict(children[i], d2['children'][0])
        else:
            ret['children'].append(d2['children'][0])
    else:
        dummy = {
            'name' : '',
            'size' : d2['size']
        }
        ret['children'].append(dummy)

    return ret

def strip_func(f):

    ret = f
    ret =  re.sub('\(\[kernel.kallsyms\]\.init\.text\)', '', ret)
    ret =  re.sub('\(\[kernel.kallsyms\]\)', '', ret)
    ret =  re.sub('\(\[unknown\]\)', '', ret)
    ret =  re.sub('\(\)', '', ret)
    ret =  ''.join(ret.split()[1:])
    return ret

for line in sys.stdin:
    if line[0] == '#':
        continue
    if line[0] == '\n':
        if not stack_trace == []:
            stack_traces.append(stack_trace)
        stack_trace = []
        continue
    if line[0] == '\t':
        stack_trace.append(line.strip())
        continue

for st in stack_traces:
    count = stack_traces.count(st) + 1
    st.reverse()
    st =  map(strip_func, st)
    stack_sample = {
        'stack_trace' : st,
        'count' : count
    }
    if not st in map(lambda x: x['stack_trace'], stack_samples):
        stack_samples.append(stack_sample)

root = {
    'name' : 'All',
    'children' : []
}

for ss in stack_samples:
    d = stack_sample_to_dict(ss)
    d = add_root(d)
    root = merge_dict(root, d)

print "var trace_json = ", root
