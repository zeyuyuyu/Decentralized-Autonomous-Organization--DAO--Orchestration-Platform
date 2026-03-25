from typing import Dict, List, Optional
from decimal import Decimal
import time

class VotingPower:
    def __init__(self, base_weight: Decimal):
        self.base_weight = base_weight
        self.time_lock = 0
        self.stake_amount = Decimal('0')
    
    def calculate_weight(self) -> Decimal:
        time_bonus = Decimal(min(self.time_lock / (365 * 24 * 3600), 2.0))
        stake_bonus = Decimal(min(self.stake_amount / 1000, 3.0))
        return self.base_weight * (1 + time_bonus) * (1 + stake_bonus)

class Proposal:
    def __init__(self, id: str, title: str, description: str, creator: str):
        self.id = id
        self.title = title
        self.description = description
        self.creator = creator
        self.votes_for = Decimal('0')
        self.votes_against = Decimal('0')
        self.start_time = time.time()
        self.end_time: Optional[int] = None
        self.executed = False

class DAOGovernance:
    def __init__(self):
        self.proposals: Dict[str, Proposal] = {}
        self.voting_powers: Dict[str, VotingPower] = {}
        self.vote_history: Dict[str, Dict[str, bool]] = {}
        self.quorum_threshold = Decimal('0.4')
        self.execution_delay = 48 * 3600  # 48 hours

    def register_voter(self, address: str, base_weight: Decimal) -> None:
        self.voting_powers[address] = VotingPower(base_weight)

    def update_stake(self, address: str, amount: Decimal) -> None:
        if address in self.voting_powers:
            self.voting_powers[address].stake_amount = amount

    def lock_tokens(self, address: str, duration: int) -> None:
        if address in self.voting_powers:
            self.voting_powers[address].time_lock = duration

    def create_proposal(self, id: str, title: str, description: str, creator: str) -> Proposal:
        if id in self.proposals:
            raise ValueError('Proposal ID already exists')
        
        proposal = Proposal(id, title, description, creator)
        self.proposals[id] = proposal
        self.vote_history[id] = {}
        return proposal

    def cast_vote(self, voter: str, proposal_id: str, support: bool) -> bool:
        if proposal_id not in self.proposals:
            raise ValueError('Invalid proposal ID')
            
        if voter not in self.voting_powers:
            raise ValueError('Voter not registered')
            
        proposal = self.proposals[proposal_id]
        
        if proposal.end_time and time.time() > proposal.end_time:
            raise ValueError('Voting period has ended')

        # Prevent double voting
        if proposal_id in self.vote_history and voter in self.vote_history[proposal_id]:
            raise ValueError('Voter has already voted on this proposal')

        voting_weight = self.voting_powers[voter].calculate_weight()
        
        if support:
            proposal.votes_for += voting_weight
        else:
            proposal.votes_against += voting_weight
            
        self.vote_history[proposal_id][voter] = support
        return True

    def get_proposal_status(self, proposal_id: str) -> Dict:
        if proposal_id not in self.proposals:
            raise ValueError('Invalid proposal ID')
            
        proposal = self.proposals[proposal_id]
        total_votes = proposal.votes_for + proposal.votes_against
        
        if total_votes == 0:
            approval_percentage = Decimal('0')
        else:
            approval_percentage = (proposal.votes_for / total_votes) * 100

        quorum_reached = total_votes >= self.quorum_threshold
        
        return {
            'id': proposal.id,
            'title': proposal.title,
            'votes_for': float(proposal.votes_for),
            'votes_against': float(proposal.votes_against),
            'approval_percentage': float(approval_percentage),
            'quorum_reached': quorum_reached,
            'executed': proposal.executed
        }

    def execute_proposal(self, proposal_id: str) -> bool:
        if proposal_id not in self.proposals:
            raise ValueError('Invalid proposal ID')
            
        proposal = self.proposals[proposal_id]
        
        if proposal.executed:
            raise ValueError('Proposal already executed')
            
        total_votes = proposal.votes_for + proposal.votes_against
        
        if total_votes < self.quorum_threshold:
            raise ValueError('Quorum not reached')
            
        if proposal.votes_for <= proposal.votes_against:
            raise ValueError('Proposal did not pass')
            
        if time.time() < proposal.start_time + self.execution_delay:
            raise ValueError('Execution delay not met')
            
        proposal.executed = True
        return True
