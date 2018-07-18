from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .db import get_similar_talks, query_talks


bp = Blueprint('talks', __name__)


@bp.route('/')
def index():
    query = {}
    fields = {'_id': 0, 'id': 1, 'published_at': 1, 'title' : 1, 'event' : 1, 'description' : 1, 'url' : 1}
    ordby  = [('published_at',-1)]
    nlimit = 10
    talks = query_talks(query, fields, ordby, nlimit)
    
    return render_template('talks/index.html', talks=talks)


@bp.route('/details/<id>', methods=('GET',))
def details(id):
    #try:
    query = {'id' : id}
    fields = {'_id': 0, 'id': 1, 'published_at': 1, 'title' : 1, 'description' : 1, 'event' : 1, 'speakers': 1, 'url' : 1}
    #fields = {}
    ordby  = [('published_at',-1)]
    nlimit = 1
    talk = query_talks(query, fields, ordby, 1)
    for t in talk:
        tid = t['id']
        event = t['event']
        desc = t['description']
        title = t['title']
        url = t['url']
        speakers = t['speakers']
    #except StopIteration:
    #    flash('Invalid talk', 'danger')
    #    return redirect(url_for('talks.index'))
    similar_talks = get_similar_talks(id)
    return render_template('talks/details.html', event=event, desc=desc, tid=tid,title=title, speakers=speakers, talk=talk, url=url, similar_talks=similar_talks)


@bp.route('/by-speaker/<id>', methods=('GET',))
def by_speaker(id):
    try:
        query = { "speakers": { "$elemMatch": { 'id': id} }}

        fields = {'_id': 0, 'speakers.first_name' : 1, 'speakers.last_name' : 1, 'speakers.description' : 1, 'speakers.bio':1}
        ordby  = [('id', 1)]
        nlimit = 1
        speaker = query_talks(query, fields, ordby, nlimit)
        for t in speaker:
            speakers = t['speakers']
            for s in speakers:
                fname = s['first_name']
                lname = s['last_name']
                desc = s['description']
                bio = s['bio']
    except StopIteration:
        flash('Invalid speaker', 'danger')
        return redirect(url_for('talks.index'))
    
    query = { "speakers": { "$elemMatch": { 'id': id} }}

    fields = {'_id': 0, 'id' : 1, 'title' : 1, 'published_at' : 1}
    ordby  = [('published_at', 1)]
    nlimit = 10
    talks = query_talks(query, fields, ordby, nlimit)
    return render_template('talks/by-speaker.html', fname=fname, lname=lname, desc=desc,speaker=speakers, bio=bio, talks=talks)
