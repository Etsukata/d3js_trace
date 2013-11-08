#!/usr/bin/python
'''
    Translate trace data to json for visualizing it with D3js.
    Usage:
        # perf script | ./d3trace.py > trace_json.js

    Copyright (C) 2013 Eiichi Tsukata <devel@etsukata.com>
'''


import sys
import re

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

def add_root(child):

    ret = {
        'name' : 'All',
        'children' : [child]
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
        print(d1)
        print 'd2:'
        print(d2)
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
    ret =  re.sub(r'\(\[kernel.kallsyms\]\.init\.text\)', '', ret)
    ret =  re.sub(r'\(\[kernel.kallsyms\]\)', '', ret)
    ret =  re.sub(r'\(\[unknown\]\)', '', ret)
    ret =  re.sub(r'\(\)', '', ret)
    ret =  ''.join(ret.split()[1:])
    return ret

def main(input_text=None):

    if input_text is None:
        input_text = sys.stdin

    stack_traces = []
    stack_trace = []
    stack_samples = []

    for line in input_text:
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
        st =  [strip_func(x) for x in st]
        stack_sample = {
            'stack_trace' : st,
            'count' : count
        }
        if not st in [x['stack_trace'] for x in stack_samples]:
            stack_samples.append(stack_sample)

    root = {
        'name' : 'All',
        'children' : []
    }

    for ss in stack_samples:
        dict_data = stack_sample_to_dict(ss)
        dict_data = add_root(dict_data)
        root = merge_dict(root, dict_data)

    return "var trace_json = " + str(root)

if __name__ == '__main__':
    output = main()
    print output
