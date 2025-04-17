import json
import os
import pandas as pd
from datetime import datetime

class XPTracker:
    def __init__(self):
        self.challenges = {}
        self.total_xp = 0
        self.xp_goal = 50000
        self.history = []

    def double_check(self):
        # Recalculate and correct all values silently
        for name, ch in self.challenges.items():
            ch['Z'] = ch['input'] // ch['required']
            ch['X'] = ch['input'] % ch['required'] if ch['required'] > 1 else 0
            ch['progress'] = f"{ch['X']}/{ch['required']} (completed {ch['Z']})" if ch['required'] > 1 else f"(completed {ch['Z']})"
        self.total_xp = sum(ch['xp'] * ch['Z'] for ch in self.challenges.values())

    def clear_challenges(self):
        """Clear all challenges and reset XP"""
        self.challenges.clear()
        self.total_xp = 0
        self.history.append({
            'action': 'clear_challenges',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self.save_data()

    def reset_progress(self, keep_challenges=True):
        if keep_challenges:
            for ch in self.challenges.values():
                ch['input'] = 0
                ch['Z'] = 0
                ch['X'] = 0
                ch['progress'] = f"0/{ch['required']} (completed 0)" if ch['required'] > 1 else "(completed 0)"
        else:
            self.challenges.clear()
        self.total_xp = 0
        # Record in history
        self.history.append({
            'action': 'reset',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'keep_challenges': keep_challenges
        })
        self.save_data()

    def create_new_challenges(self, challenge_list, earned_xp=0):
        self.challenges.clear()
        self.total_xp = earned_xp
        for ch in challenge_list:
            self.challenges[ch['name']] = {
                'xp': ch['xp'],
                'required': ch['required'],
                'input': 0,
                'Z': 0,
                'X': 0,
                'progress': f"0/{ch['required']} (completed 0)" if ch['required'] > 1 else "(completed 0)"
            }
        # Record in history
        self.history.append({
            'action': 'create_challenges',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'challenges': challenge_list,
            'earned_xp': earned_xp
        })
        self.save_data()

    def use_default_challenges(self, earned_xp=0):
        default_challenges = [
            {'name': 'Fenix kills', 'xp': 2500, 'required': 5},
            {'name': 'Kobra sights', 'xp': 1000, 'required': 2},
            {'name': 'OKP-7 sights', 'xp': 1500, 'required': 1}
        ]
        self.create_new_challenges(default_challenges, earned_xp)

    def update_progress(self, updates):
        for name, count in updates.items():
            if name in self.challenges:
                # Allow for negative counts for decrements, but don't go below zero
                if count < 0 and self.challenges[name]['input'] + count < 0:
                    # Just set to zero if trying to decrement below zero
                    self.challenges[name]['input'] = 0
                else:
                    self.challenges[name]['input'] += count
        self.double_check()
        # Record in history
        self.history.append({
            'action': 'update',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'updates': updates
        })
        self.save_data()

    def get_progress_data(self):
        """Get progress data for visualization"""
        data = []
        for name, ch in self.challenges.items():
            completion_percent = min(100, (ch['input'] / ch['required']) * 100) if ch['required'] > 0 else 0
            data.append({
                'challenge': name,
                'completion': completion_percent,
                'xp_earned': ch['xp'] * ch['Z'],
                'completions': ch['Z'],
                'current_progress': ch['X'],
                'required': ch['required']
            })
        return pd.DataFrame(data)

    def get_summary(self):
        """Get summary statistics"""
        return {
            'total_xp': self.total_xp,
            'xp_goal': self.xp_goal,
            'remaining_xp': max(0, self.xp_goal - self.total_xp),
            'progress_percent': min(100, (self.total_xp / self.xp_goal) * 100) if self.xp_goal > 0 else 0,
            'challenge_count': len(self.challenges)
        }

    def set_xp_goal(self, goal):
        self.xp_goal = goal
        # Record in history
        self.history.append({
            'action': 'set_goal',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'goal': goal
        })
        self.save_data()

    def save_data(self):
        """Save tracker data to file"""
        data = {
            'challenges': self.challenges,
            'total_xp': self.total_xp,
            'xp_goal': self.xp_goal,
            'history': self.history
        }
        with open('xp_tracker_data.json', 'w') as f:
            json.dump(data, f)

    def load_data(self):
        """Load tracker data from file"""
        if os.path.exists('xp_tracker_data.json'):
            try:
                with open('xp_tracker_data.json', 'r') as f:
                    data = json.load(f)
                    self.challenges = data.get('challenges', {})
                    self.total_xp = data.get('total_xp', 0)
                    self.xp_goal = data.get('xp_goal', 50000)
                    self.history = data.get('history', [])
                return True
            except Exception as e:
                print(f"Error loading data: {e}")
                return False
        return False
