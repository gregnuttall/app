"""
Routing for the application.

This is essentially the controllers for the application in terms of MVC, but all in one.
"""

from functools import cmp_to_key
import os
import re
import unicodedata

from flask import render_template, flash, redirect, request, url_for, g, abort, make_response
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy  import asc
from sqlalchemy.exc import IntegrityError

from lego import app, db, lm
from lego.forms import LoginForm, ScoreRoundForm, EditTeamForm, NewTeamForm, EditTeamScoreForm, ResetTeamScoreForm, StageForm, generate_manage_active_teams_form
from lego.models import User, Team
import lego.util as util


@app.before_request
def before_request():
    """
    Set up user global.
    """
    g.user = current_user


@app.context_processor
def override_url_for():
    """
    Override for addding a cache buster to static assets.
    """
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    """
    Append a cache buster to static assets.

    Based on: <http://flask.pocoo.org/snippets/40/>
    """
    if endpoint == 'static':
        filename = values.get('filename', None)

        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)

    return url_for(endpoint, **values)


@app.after_request
def after_request(response):
    """
    Log all requests.
    """
    app.logger.info('%s %s %s %s %s',
                    request.remote_addr,
                    request.method,
                    request.scheme,
                    request.full_path,
                    response.status)
    return response


@app.template_filter('slugify')
def slugify(value: str):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    Based on: <https://gist.github.com/berlotto/6295018>.
    """
    if not value:
        return ''

    strip_re = re.compile(r'[^\w\s-]')
    hyphenate_re = re.compile(r'[-\s]+')

    normalised_value = str(unicodedata.normalize('NFKD', value))
    strip_value = strip_re.sub('', str(normalised_value)).strip().lower()
    hyphenate_value = hyphenate_re.sub('-', strip_value)

    return hyphenate_value


@app.errorhandler(403)
def permission_denied(error):
    """
    403 (permission denied) error handler.
    """
    return render_template('errors/403.html', title='Permission denied'), 403


@app.errorhandler(404)
def page_not_found(error):
    """
    404 (page not found) error handler.
    """
    return render_template('errors/404.html', title='Page not found'), 404


@app.errorhandler(Exception)
def internal_server_error(exc):
    """
    500 (internal error) error handler.
    """
    app.logger.exception(exc)
    return render_template('errors/500.html', title='Internal error'), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page
    """
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        res = User.authenticate(username, password)

        if isinstance(res, User):
            login_user(res)
            return redirect(url_for('home'))

        flash(res)

    return render_template('login.html', title='Log in', form=form)


@app.route('/logout')
@login_required
def logout():
    """
    Logout page.

    Not strictly a page as it immediately redirects.
    """
    logout_user()
    return redirect(url_for('home'))


@app.route('/')
@app.route('/home')
def home():
    """
    Home page.
    """
    teams = Team.query.filter_by(is_practice=False).order_by(asc('number')).all()
    return render_template('home.html', title='Home', teams=teams)


@app.route('/scoreboard/', defaults={'offset': 0})
@app.route('/scoreboard/<int:offset>')
def scoreboard(offset):
    teams = Team.query.filter_by(active=True, is_practice=False).all()
    teams = sorted(teams, key=cmp_to_key(util.compare_teams))
    stage = app.load_stage()
    params = {
        'title': 'Scoreboard',
        'stage': stage,
        'offset': offset,
        'end': len(teams)
    }

    if app.config['LEGO_APP_TYPE'] in ('bristol', 'uk'):
        template = 'scoreboard_{!s}.html'.format(app.config['LEGO_APP_TYPE'])
    else:
        raise Exception('Unsupported value for LEGO_APP_TYPE: {!s}' \
                        .format(app.config['LEGO_APP_TYPE']))

    stages = ('round_1', 'round_2', 'quarter_final', 'semi_final', 'final')
    for i, s in enumerate(stages):
        if stage >= i:
            params[s] = True

    if stage == 0:
        if app.config['LEGO_APP_TYPE'] == 'bristol':
            quotient = len(teams) // 3
            remainder = len(teams) % 3

            # remainder == 0
            if not remainder:
                params['first'] = teams[:quotient]
                params['second'] = teams[quotient:(quotient * 2)]
                params['third'] = teams[(quotient * 2):]

            elif remainder == 1:
                params['first'] = teams[:(quotient + 1)]
                params['second'] = teams[quotient + 1:(quotient * 2) + 1]
                params['third'] = teams[(quotient * 2) + 1:]

            # remainder == 2
            else:
                params['first'] = teams[:(quotient)]
                params['second'] = teams[quotient:(quotient * 2) + 1]
                params['third'] = teams[(quotient * 2) + 1:]

            return render_template(template, **params)
        else:
            params['teams'] = teams[offset:offset + 10]
            return render_template(template, **params)

    # force offset to 0 if we refreshed in the middle of a cycle
    if params['offset'] != 0:
        return redirect(url_for('scoreboard'))

    if app.config['LEGO_APP_TYPE'] == 'bristol':
        params['first'] = teams
    else:
        params['teams'] = teams
        params['no_pagination'] = True

    return render_template(template, **params)


@app.route('/judges/')
@app.route('/judges')
@login_required
def judges_home():
    if not (current_user.is_judge or current_user.is_admin):
        return abort(403)

    teams = Team.query.filter_by(is_practice=False).all()
    teams = sorted(teams, key=cmp_to_key(util.compare_teams))

    show_round_2 = app.config['LEGO_APP_TYPE'] == 'uk'

    return render_template('judges/home.html', title='Judges - Home', teams=teams,
                           show_round_2=show_round_2)


@app.route('/judges/export')
@login_required
def judges_export():
    if not(current_user.is_judge or current_user.is_admin):
        return abort(403)

    teams = Team.query.filter_by(is_practice=False).all()
    teams = sorted(teams, key=cmp_to_key(util.compare_teams))

    headers = ['Rank', 'Number', 'Name', 'Round 1 - Attempt 1', 'Round 1 - Attempt 2',
               'Round 1 - Attempt 3', 'Round 1 - Best', 'Round 2', 'Quarter Final', 'Semi Final',
               'Final 1', 'Final 2', 'Final Total']
    columns = ['number', 'name', 'attempt_1', 'attempt_2', 'attempt_3', 'best_attempt', 'round_2',
               'quarter', 'semi', 'final_1', 'final_2', 'final_total']

    csv_parts = []
    csv_parts.append(','.join(headers))

    for i, t in enumerate(teams, start=1):
        row = [str(i)]

        for c in columns:
            x = getattr(t, c)

            if x is None:
                x = ''

            x = str(x)
            row.append(x)

        csv_parts.append(','.join(row))

    resp = make_response('\n'.join(csv_parts))

    resp.headers['Content-Type'] = 'text/csv'
    resp.headers['Content-Disposition'] = 'attachment; filename="teams.csv"'
    resp.headers['Content-Transfer-Encoding'] = 'binary'
    resp.headers['Accept-Ranges'] = 'bytes'
    resp.headers['Cache-Control'] = 'private'
    resp.headers['Pragma'] = 'private'
    # the exact date doesn't matter here as long as it's in the past so it
    # expires immediately and a browser won't try and cache it
    resp.headers['Expires'] = 'Mon, 26 Jul 1997 05:00:00 GMT'

    app.logger.info(resp)
    app.logger.info(resp.headers)

    return resp


@app.route('/judges/score_round', methods=['GET', 'POST'])
@login_required
def judges_score_round():
    if not (current_user.is_judge or current_user.is_admin):
        return abort(403)

    form = ScoreRoundForm()

    teams = Team.query.filter_by(active=True).order_by('number').all()
    form.team.choices = [('', '--Select team--')]
    form.team.choices += [(str(t.id), t.name) for t in teams]

    if form.validate_on_submit():
        team_id = form.team.data
        team = Team.query.get(team_id)
        score = form.points_scored()

        if form.confirm.data == '1':
            try:
                team.set_score(score)
            except Exception as exc:
                flash(str(exc))
            else:
                db.session.commit()

                flash('Submitted for team: {!s}, score: {!s}.' \
                      .format(team.name, score[0]))

                return redirect(url_for('judges_score_round'))

        # don't set confirm in the form if this is a practice attempt
        if team.is_practice:
            flash('Practice attempt')
        else:
            form.confirm.data = '1'

        flash('Score: {!s}'.format(score[0]))

        # data submitted to the form overrides whatever we set as data here
        # so we have to override that if something changed after the
        # initial confirmation
        if form.score.raw_data:
            form.score.raw_data[0] = score[0]
        else:
            form.score.data = score[0]

        return render_template('judges/score_round.html', title='Score Round',
                               form=form, confirm=True)

    return render_template('judges/score_round.html', title='Score Round', form=form)

@app.route('/admin/team')
@login_required
def admin_team():
    if not current_user.is_admin:
        return abort(403)

    teams = Team.query.filter_by(is_practice=False).order_by('number')

    return render_template('admin/team.html', title='Teams', teams=teams)


@app.route('/admin/team/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_team_edit(id: int):
    if not current_user.is_admin:
        return abort(403)

    team = Team.query.filter_by(id=id).first()
    form = EditTeamForm()

    if form.validate_on_submit():
        try:
            team.number = form.number.data
            team.name = form.name.data
            db.session.commit()

        except IntegrityError as e:
            app.logger.exception(e)
            db.session.rollback()
            flash('The name or number requested is already in use. Please use another one.')

        except Exception as e:
            app.logger.exception(e)
            db.session.rollback()
            flash('An unknown error occurred. See the logs for more information')

        else:
            flash('Team details successfully updated')
            return redirect(url_for('admin_team'))

    form.id.data = team.id
    form.name.data = team.name
    form.number.data = team.number

    return render_template('admin/team_edit.html', title='Edit Team', form=form)

@app.route('/admin/team/new', methods=['GET', 'POST'])
@login_required
def admin_team_new():
    if not current_user.is_admin:
        return abort(403)

    form = NewTeamForm()

    if form.validate_on_submit():
        try:
            team = Team(number=form.number.data, name=form.name.data)
            db.session.add(team)
            db.session.commit()

        except IntegrityError as e:
            app.logger.exception(e)
            db.session.rollback()
            flash('The name or number requested is already in use. Please use another one.')

        except Exception as e:
            app.logger.exception(e)
            db.session.rollback()
            flash('An unknown error occurred. See the logs for more information')
        else:
            flash('Team details successfully updated')
            return redirect(url_for('admin_team'))

    return render_template('admin/team_new.html', title='New Team', form=form)

@app.route('/admin/team/<int:id>/score/edit', methods=['GET', 'POST'])
@login_required
def admin_team_score_edit(id: int):
    if not current_user.is_admin:
        return abort(403)

    team = Team.query.filter_by(id=id).first()
    form = EditTeamScoreForm()

    if form.validate_on_submit():
        try:
            team.edit_round_score(form.stage.data, form.score.data)
            db.session.commit()

        except Exception as e:
            app.logger.exception(e)
            db.session.rollback()
            flash('An unknown error occurred. See the logs for more information')

        else:
            flash('Team score successfully updated')
            return redirect(url_for('admin_team'))

    form.id.data = team.id
    form.score.data = 0

    return render_template('admin/team_score_edit.html', title='Edit Team Score', form=form)

@app.route('/admin/team/<int:id>/score/reset', methods=['GET', 'POST'])
@login_required
def admin_team_score_reset(id: int):
    """
    For resetting a team's score for a specific round.
    """
    if not current_user.is_admin:
        return abort(403)

    team = Team.query.filter_by(id=id).first()
    form = ResetTeamScoreForm()

    if form.validate_on_submit():
        try:
            team.reset_round_score(form.stage.data)
            db.session.commit()

        except Exception as e:
            app.logger.exception(e)
            db.session.rollback()
            flash('An unknown error occurred. See the logs for more information')

        else:
            flash('Team score successfully reset')
            return redirect(url_for('admin_team'))

    form.id.data = team.id

    return render_template('admin/team_score_reset.html', title='Reset Team Score', form=form)


@app.route('/admin/stage', methods=['GET', 'POST'])
@login_required
def admin_stage():
    """
    For moving the stage forward.
    """
    if not current_user.is_admin:
        return abort(403)

    stages = ('First Round', 'Second Round', 'Quarter Final', 'Semi Final', 'Final')

    stage = app.load_stage()
    current_stage = stages[stage]

    form = StageForm()

    if form.validate_on_submit():
        new_stage = int(form.stage.data)
        cur_file_path = os.path.dirname(os.path.abspath(__file__))

        if new_stage <= stage:
            flash('Unable to go back a stage.')

        if app.config['LEGO_APP_TYPE'] == 'bristol' and new_stage == 1:
            flask('Round 2 only available during UK Final.')
        else:
            set_active_teams(new_stage)

            with open(os.path.join(cur_file_path, 'tmp', '.stage'), 'w') as fh:
                fh.write(str(new_stage))

            flash('Stage updated to: {!s}'.format(stages[int(new_stage)]))
            return redirect(url_for('admin_stage'))

    return render_template('admin/stage.html', title='Manage Stage', form=form,
                           current_stage=current_stage)


def set_active_teams(stage):
    """
    Helper for setting the active teams after a stage has been moved forward.
    """
    teams = Team.query.filter_by(active=True, is_practice=False).all()
    teams = sorted(teams, key=cmp_to_key(util.compare_teams))

    if app.config['LEGO_APP_TYPE'] == 'bristol':
        for i, team in enumerate(teams):
            if stage == 2 and i >= 6:
                team.active = False

            if stage == 3 and i >= 4:
                team.active = False

            if stage == 4 and i >= 2:
                team.active = False

    elif app.config['LEGO_APP_TYPE'] == 'uk':
        for i, team in enumerate(teams):
            if stage == 1 and i >= 12:
                team.active = False

            if stage == 2 and i >= 8:
                team.active = False

            if stage == 3 and i >= 4:
                team.active = False

            if stage == 4 and i >= 2:
                team.active = False

    db.session.commit()


@app.route('/admin/manage_active_teams', methods=['GET', 'POST'])
def admin_manage_active_teams():
    """
    For managing active teams if the automatic setting is not sufficient.
    """
    if not current_user.is_admin:
        return abort(403)

    form = generate_manage_active_teams_form()

    if form.validate_on_submit():
        for t in form.teams:
            is_active = form[str(t.id) + '_active'].data
            t.active = is_active

        db.session.commit()

    return render_template('admin/manage_active_teams.html', title='Manage Active Teams',
                           form=form)
