import web3
from typing import List, Tuple

class DAOGovernance:
    def __init__(self, dao_address: str, web3_provider: web3.Web3):
        self.dao_address = dao_address
        self.web3 = web3_provider
        self.dao_contract = self.web3.eth.contract(address=dao_address, abi=self.get_abi())

    def get_abi(self) -> List[dict]:
        # Load the ABI from a file or retrieve it from the blockchain
        with open('dao_abi.json', 'r') as f:
            return json.load(f)

    def create_proposal(self, title: str, description: str, vote_duration: int) -> int:
        """
        Create a new proposal in the DAO.
        
        Args:
            title (str): The title of the proposal.
            description (str): The description of the proposal.
            vote_duration (int): The duration of the voting period in blocks.
        
        Returns:
            int: The ID of the newly created proposal.
        """
        tx = self.dao_contract.functions.createProposal(title, description, vote_duration).transact()
        receipt = self.web3.eth.waitForTransactionReceipt(tx)
        return receipt.logs[0].args.proposalId

    def vote(self, proposal_id: int, vote: bool) -> None:
        """
        Vote on a proposal in the DAO.
        
        Args:
            proposal_id (int): The ID of the proposal to vote on.
            vote (bool): True for 'yes', False for 'no'.
        """
        tx = self.dao_contract.functions.vote(proposal_id, vote).transact()
        self.web3.eth.waitForTransactionReceipt(tx)

    def get_proposal_details(self, proposal_id: int) -> Tuple[str, str, int, int, int, bool]:
        """
        Get the details of a proposal in the DAO.
        
        Args:
            proposal_id (int): The ID of the proposal to retrieve.
        
        Returns:
            Tuple[str, str, int, int, int, bool]: The proposal's title, description, vote duration, start block, end block, and whether it has been executed.
        """
        proposal = self.dao_contract.functions.proposals(proposal_id).call()
        return (
            proposal[0],
            proposal[1],
            proposal[2],
            proposal[3],
            proposal[4],
            proposal[5]
        )
