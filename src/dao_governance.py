# DAO Governance System with Quadratic Funding
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime
import math

@dataclass
class Proposal:
    id: str
    title: str
    description: str
    creator: str
    created_at: datetime
    voting_ends_at: datetime
    requested_funds: float
    votes: Dict[str, float] = None
    
    def __post_init__(self):
        if self.votes is None:
            self.votes = {}

class DAOGovernance:
    def __init__(self, total_funding_pool: float):
        self.proposals: Dict[str, Proposal] = {}
        self.funding_pool = total_funding_pool
        self.token_holdings: Dict[str, float] = {}
    
    def create_proposal(self, id: str, title: str, description: str, 
                       creator: str, duration_days: int, requested_funds: float) -> Proposal:
        proposal = Proposal(
            id=id,
            title=title, 
            description=description,
            creator=creator,
            created_at=datetime.now(),
            voting_ends_at=datetime.now().replace(day=datetime.now().day + duration_days),
            requested_funds=requested_funds
        )
        self.proposals[id] = proposal
        return proposal

    def vote(self, voter: str, proposal_id: str, tokens: float) -> bool:
        if proposal_id not in self.proposals:
            raise ValueError('Invalid proposal ID')
            
        proposal = self.proposals[proposal_id]
        if datetime.now() > proposal.voting_ends_at:
            raise ValueError('Voting period has ended')
            
        if tokens > self.token_holdings.get(voter, 0):
            raise ValueError('Insufficient tokens')
            
        # Record the vote using quadratic voting weight
        proposal.votes[voter] = math.sqrt(tokens)
        return True
        
    def calculate_quadratic_funding(self) -> Dict[str, float]:
        results = {}
        total_sqrt_votes = 0
        
        # Calculate the sum of square roots of votes
        for proposal in self.proposals.values():
            sqrt_sum = sum(proposal.votes.values())
            squared_sum = sqrt_sum * sqrt_sum
            results[proposal.id] = squared_sum
            total_sqrt_votes += squared_sum
            
        # Normalize allocations to funding pool
        funding_ratio = self.funding_pool / total_sqrt_votes if total_sqrt_votes > 0 else 0
        
        for proposal_id in results:
            results[proposal_id] = min(
                results[proposal_id] * funding_ratio,
                self.proposals[proposal_id].requested_funds
            )
            
        return results
    
    def get_proposal_status(self, proposal_id: str) -> Dict:
        if proposal_id not in self.proposals:
            raise ValueError('Invalid proposal ID')
            
        proposal = self.proposals[proposal_id]
        funding = self.calculate_quadratic_funding().get(proposal_id, 0)
        
        return {
            'id': proposal.id,
            'title': proposal.title,
            'votes': len(proposal.votes),
            'vote_power': sum(proposal.votes.values()),
            'allocated_funding': funding,
            'status': 'active' if datetime.now() <= proposal.voting_ends_at else 'ended'
        }

    def register_tokens(self, holder: str, amount: float) -> None:
        """Register token holdings for voting power"""
        self.token_holdings[holder] = self.token_holdings.get(holder, 0) + amount