import time
import hashlib
import json

class DAOGovernance:
    def __init__(self, dao_members, initial_proposals):
        self.dao_members = dao_members
        self.proposals = initial_proposals
        self.vote_counts = {p['id']: 0 for p in self.proposals}
        self.executed_proposals = []

    def submit_proposal(self, proposal):
        proposal_id = hashlib.sha256(json.dumps(proposal).encode()).hexdigest()
        self.proposals.append({'id': proposal_id, 'details': proposal})
        self.vote_counts[proposal_id] = 0
        return proposal_id

    def cast_vote(self, member, proposal_id, vote):
        if member not in self.dao_members:
            raise ValueError('Member is not part of the DAO')
        if proposal_id not in self.vote_counts:
            raise ValueError('Proposal does not exist')
        self.vote_counts[proposal_id] += 1 if vote else -1

    def execute_proposals(self):
        for proposal in self.proposals:
            proposal_id = proposal['id']
            if self.vote_counts[proposal_id] >= (len(self.dao_members) // 2) + 1:
                self.executed_proposals.append(proposal)
                self.proposals.remove(proposal)
                del self.vote_counts[proposal_id]
                print(f'Executed proposal: {proposal["details"]}')
        time.sleep(60)  # Wait for 1 minute before checking again
