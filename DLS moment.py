from dataclasses import dataclass
from typing import List, Dict, Tuple
import pandas as pd

@dataclass
class Team:
    id: str
    name: str
    continent: str
    region: str
    
   
    national_rankings: List[float]  
    continental_participations: List[Dict[str, float]]  
    international_ranking: float
    

    arena_capacity: float
    arena_modernity: float
    training_facilities: float
    auxiliary_platforms: float
    airport_accessibility: float
    railway_accessibility: float
    other_transport: float
    
 
    budget: float
    required_budget: float
    sponsorship_strength: float
    media_partnership: float
    financial_fair_play: List[float]  
    
    # Marketing Potential data
    social_media_following: float
    average_attendance: float
    regional_market_size: float
    tv_broadcast_reach: float
    digital_media_presence: float
    tourism_attractiveness: float
    cultural_significance: float
    international_accessibility: float
    
    # Organizational Experience data
    international_events: List[Tuple[float, float]] 
    management_qualification: float
    communication_service: float
    local_authority_partnership: float
    sports_federation_partnership: float

class GSLTeamSelector:
    def __init__(self, 
                 teams: List[Team],
                 main_weights: Dict[str, float] = None,
                 sub_weights: Dict[str, Dict[str, float]] = None,
                 max_values: Dict[str, float] = None):
        
        self.teams = teams
        
        # Default main criteria weights
        self.main_weights = main_weights or {
            "sporting_level": 0.30,
            "infrastructure": 0.15,
            "financial_stability": 0.20,
            "geographic_representation": 0.10,
            "marketing_potential": 0.15,
            "organizational_experience": 0.10
        }
        
        # Default sub-weights
        self.sub_weights = sub_weights or {
            "sporting_level": {"national": 0.4, "continental": 0.4, "international": 0.2},
            "infrastructure": {"arena": 0.5, "training": 0.3, "transport": 0.2},
            "financial_stability": {"budget": 0.5, "sponsorship": 0.3, "fair_play": 0.2},
            "geographic_representation": {"continental": 0.6, "regional": 0.4},
            "marketing_potential": {"fan_base": 0.5, "promotion": 0.3, "city": 0.2},
            "organizational_experience": {"hosting": 0.5, "management": 0.3, "partnership": 0.2},
            
            # Additional sub-sub-weights
            "transport": {"airport": 0.6, "railway": 0.3, "other": 0.1},
            "fan_base": {"social_media": 0.5, "attendance": 0.5},
            "national_temporal": [0.30, 0.25, 0.20, 0.15, 0.10], 
            "continental_temporal": [0.30, 0.25, 0.20, 0.15, 0.10],  
            "ffp_temporal": [0.30, 0.25, 0.20, 0.15, 0.10] 
        }
        
        
        self.max_values = max_values or {
            "social_media": 20000000,  # 20M followers
            "attendance": 15000,       # 15K average attendance
            "int_events_score": 10     # Maximum international event score
        }
        
        # Selected teams tracking
        self.selected_teams = []
        self.continent_counts = {}
        
        # Calculate scores
        self.team_scores = {}
        self.calculate_all_scores()
        
    def calculate_all_scores(self):
        """Calculate scores for all teams"""
        for team in self.teams:
            self.team_scores[team.id] = self.calculate_team_score(team)
    
    def calculate_team_score(self, team: Team) -> float:
        """Calculate the overall score for a team"""
        scores = {
            "sporting_level": self.calculate_sporting_level(team),
            "infrastructure": self.calculate_infrastructure(team),
            "financial_stability": self.calculate_financial_stability(team),
            "geographic_representation": self.calculate_geographic_representation(team),
            "marketing_potential": self.calculate_marketing_potential(team),
            "organizational_experience": self.calculate_organizational_experience(team)
        }
        
        # Calculate weighted sum of scores
        total_score = sum(self.main_weights[key] * scores[key] for key in scores)
        
        # Apply geographic penalty (not applicable in initial scoring)
        # This will be applied during the selection process
        
        return total_score
    
    def calculate_sporting_level(self, team: Team) -> float:
        """Calculate Sporting Level component score"""
        
        national_weights = self.sub_weights["national_temporal"]
        national_score = sum(w * r for w, r in zip(national_weights, team.national_rankings)) / sum(national_weights)
        
        # Continental tournament participation
        continental_weights = self.sub_weights["continental_temporal"]
        cont_scores = []
        for season_idx, season_tournaments in enumerate(team.continental_participations):
            season_score = sum(level * importance 
                              for tournament, level in season_tournaments.items() 
                              for importance in [0.7 if tournament == "Euroleague" else 0.5])
            cont_scores.append(season_score)
        
        max_season_score = 1.0  # Normalized maximum
        continental_score = sum(w * score for w, score in zip(continental_weights, cont_scores)) / sum(continental_weights) / max_season_score
        continental_score = min(1.0, continental_score)  
        
        
        max_rank = 100  
        international_score = (max_rank - team.international_ranking + 1) / max_rank
        
    
        sl_weights = self.sub_weights["sporting_level"]
        sporting_level_score = (sl_weights["national"] * national_score + 
                              sl_weights["continental"] * continental_score + 
                              sl_weights["international"] * international_score)
        
        return sporting_level_score
    
    def calculate_infrastructure(self, team: Team) -> float:
        """Calculate Infrastructure component score"""
      
        min_capacity = 5000
        ideal_capacity = 8000
        capacity_score = min(1.0, (team.arena_capacity - min_capacity) / (ideal_capacity - min_capacity))
        arena_score = 0.7 * capacity_score + 0.3 * team.arena_modernity
        
      
        training_score = (team.training_facilities + team.auxiliary_platforms) / 2
        
        # Transport accessibility
        transport_weights = self.sub_weights["transport"]
        transport_score = (transport_weights["airport"] * team.airport_accessibility + 
                         transport_weights["railway"] * team.railway_accessibility + 
                         transport_weights["other"] * team.other_transport)
        
        # Combine using sub-weights
        infra_weights = self.sub_weights["infrastructure"]
        infrastructure_score = (infra_weights["arena"] * arena_score + 
                              infra_weights["training"] * training_score + 
                              infra_weights["transport"] * transport_score)
        
        return infrastructure_score
    
    def calculate_financial_stability(self, team: Team) -> float:
        """Calculate Financial Stability component score"""
        # Budget adequacy
        budget_score = min(1.0, team.budget / team.required_budget)
        
        # Sponsorship and media partnerships
        sponsorship_score = (team.sponsorship_strength + team.media_partnership) / 2
        
        # Financial fair play
        ffp_weights = self.sub_weights["ffp_temporal"]
        ffp_score = sum(w * score for w, score in zip(ffp_weights, team.financial_fair_play)) / sum(ffp_weights)
        
        # Combine using sub-weights
        fs_weights = self.sub_weights["financial_stability"]
        financial_stability_score = (fs_weights["budget"] * budget_score + 
                                  fs_weights["sponsorship"] * sponsorship_score + 
                                  fs_weights["fair_play"] * ffp_score)
        
        return financial_stability_score
    
    def calculate_geographic_representation(self, team: Team) -> float:
        """Calculate Geographic Representation component score"""
        # This component depends on already selected teams, so it's recalculated during selection
        # For initial scoring, we assume no teams are selected yet
        
        # Count teams per continent in current selection
        continent_count = self.continent_counts.get(team.continent, 0)
        
        # Count teams per region in current selection
        region_count = sum(1 for t in self.selected_teams if t.region == team.region)
        
        # Calculate scores
        continental_score = 1.0 / (continent_count + 1)
        regional_score = 1.0 / (region_count + 1)
        
        # Combine using sub-weights
        gr_weights = self.sub_weights["geographic_representation"]
        geographic_score = (gr_weights["continental"] * continental_score + 
                          gr_weights["regional"] * regional_score)
        
        return geographic_score
    
    def calculate_marketing_potential(self, team: Team) -> float:
        """Calculate Marketing Potential component score"""
        # Fan base size and activity
        social_media_score = min(1.0, team.social_media_following / self.max_values["social_media"])
        attendance_score = min(1.0, team.average_attendance / self.max_values["attendance"])
        
        fan_weights = self.sub_weights["fan_base"]
        fan_score = fan_weights["social_media"] * social_media_score + fan_weights["attendance"] * attendance_score
        
        promotion_score = (team.regional_market_size + team.tv_broadcast_reach + team.digital_media_presence) / 3
        
     
        city_score = (team.tourism_attractiveness + team.cultural_significance + team.international_accessibility) / 3
        
        mp_weights = self.sub_weights["marketing_potential"]
        marketing_score = (mp_weights["fan_base"] * fan_score + 
                         mp_weights["promotion"] * promotion_score + 
                         mp_weights["city"] * city_score)
        
        return marketing_score
    
    def calculate_organizational_experience(self, team: Team) -> float:
        """Calculate Organizational Experience component score"""
        # International event hosting experience
        events_score = sum(importance * quality for importance, quality in team.international_events)
        events_score = min(1.0, events_score / self.max_values["int_events_score"])
        
        # Management quality
        management_score = (team.management_qualification + team.communication_service) / 2
        
        # Partnership score
        partnership_score = (team.local_authority_partnership + team.sports_federation_partnership) / 2
        
        oe_weights = self.sub_weights["organizational_experience"]
        org_exp_score = (oe_weights["hosting"] * events_score + 
                       oe_weights["management"] * management_score + 
                       oe_weights["partnership"] * partnership_score)
        
        return org_exp_score
    
    def apply_geographic_penalty(self, team: Team, penalty_weight: float = 0.2) -> float:
        """Calculate geographic penalty based on continent representation"""
        continent_count = self.continent_counts.get(team.continent, 0)
        
        if continent_count < 2:
            return 0
        else:
            return penalty_weight * (continent_count - 1)
    
    def select_teams(self, num_teams: int = 20) -> List[Team]:
        """Select teams for the league using the calculated scores"""
        self.selected_teams = []
        self.continent_counts = {}
        
        # First, ensure at least 2 teams from each continent
        continents = set(team.continent for team in self.teams)
        
        for continent in continents:
            # Get teams from this continent
            continent_teams = [t for t in self.teams if t.continent == continent]
            
            # Sort by score
            continent_teams.sort(key=lambda t: self.team_scores[t.id], reverse=True)
            
            # Take top 2 (or all if less than 2)
            top_teams = continent_teams[:min(2, len(continent_teams))]
            
            for team in top_teams:
                self.selected_teams.append(team)
                self.continent_counts[team.continent] = self.continent_counts.get(team.continent, 0) + 1
        
        # Then fill remaining slots with highest-scoring teams
        remaining_slots = num_teams - len(self.selected_teams)
        
        # Get all unselected teams
        unselected_teams = [t for t in self.teams if t not in self.selected_teams]
        
        # Recalculate scores with geographic penalties
        adjusted_scores = {}
        for team in unselected_teams:
            base_score = self.team_scores[team.id]
            penalty = self.apply_geographic_penalty(team)
            adjusted_scores[team.id] = base_score - penalty
        
        # Sort by adjusted score
        unselected_teams.sort(key=lambda t: adjusted_scores[t.id], reverse=True)
        
        # Add top remaining teams
        for team in unselected_teams[:remaining_slots]:
            self.selected_teams.append(team)
            self.continent_counts[team.continent] = self.continent_counts.get(team.continent, 0) + 1
        
        return self.selected_teams
    
    def get_team_scores_df(self) -> pd.DataFrame:
        """Return a DataFrame with all team scores for analysis"""
        data = []
        
        for team in self.teams:
            team_data = {
                "team_id": team.id,
                "team_name": team.name,
                "continent": team.continent,
                "region": team.region,
                "overall_score": self.team_scores[team.id],
                "sporting_level": self.calculate_sporting_level(team),
                "infrastructure": self.calculate_infrastructure(team),
                "financial_stability": self.calculate_financial_stability(team),
                "geographic_representation": self.calculate_geographic_representation(team),
                "marketing_potential": self.calculate_marketing_potential(team),
                "organizational_experience": self.calculate_organizational_experience(team)
            }
            data.append(team_data)
        
        return pd.DataFrame(data)


# Example usage with sample data
def create_sample_teams():
    """Create sample team data for demonstration"""
    teams = []
    
    # Real Madrid (example of a top European team)
    real_madrid = Team(
        id="RM", 
        name="Real Madrid", 
        continent="Europe", 
        region="Western Europe",
        
       
        national_rankings=[1.0, 0.9, 1.0, 0.9, 0.95],  # Top performances
        continental_participations=[
            {"Euroleague": 0.9}, {"Euroleague": 1.0}, {"Euroleague": 0.9}, 
            {"Euroleague": 0.85}, {"Euroleague": 0.9}
        ],
        international_ranking=3,
        
        arena_capacity=11000,
        arena_modernity=0.95,
        training_facilities=0.95,
        auxiliary_platforms=0.90,
        airport_accessibility=0.95,
        railway_accessibility=0.90,
        other_transport=0.85,
        
        budget=15000000,
        required_budget=10000000,
        sponsorship_strength=0.95,
        media_partnership=0.90,
        financial_fair_play=[0.95, 0.95, 0.90, 0.95, 0.95],
        
       
        social_media_following=15000000,
        average_attendance=10000,
        regional_market_size=0.95,
        tv_broadcast_reach=0.90,
        digital_media_presence=0.95,
        tourism_attractiveness=0.90,
        cultural_significance=0.95,
        international_accessibility=0.90,
        
        # Organizational Experience data (extensive)
        international_events=[(0.9, 0.95), (0.8, 0.9), (0.7, 0.95)],
        management_qualification=0.90,
        communication_service=0.95,
        local_authority_partnership=0.85,
        sports_federation_partnership=0.90
    )
    teams.append(real_madrid)
    
    # Al Ahly (example of a top African team)
    al_ahly = Team(
        id="AH", 
        name="Al Ahly SC", 
        continent="Africa", 
        region="North Africa",
        
        
        national_rankings=[1.0, 0.95, 1.0, 0.95, 1.0],  
        continental_participations=[
            {"FIBA Africa": 0.85}, {"FIBA Africa": 0.80}, {"FIBA Africa": 0.85}, 
            {"FIBA Africa": 0.75}, {"FIBA Africa": 0.80}
        ],
        international_ranking=45,
        
       
        arena_capacity=7000,
        arena_modernity=0.75,
        training_facilities=0.70,
        auxiliary_platforms=0.65,
        airport_accessibility=0.80,
        railway_accessibility=0.75,
        other_transport=0.70,
        
        # Financial Stability data (solid)
        budget=8000000,
        required_budget=7000000,
        sponsorship_strength=0.80,
        media_partnership=0.75,
        financial_fair_play=[0.85, 0.80, 0.85, 0.80, 0.75],
        
        # Marketing Potential data (strong regionally)
        social_media_following=5000000,
        average_attendance=6000,
        regional_market_size=0.85,
        tv_broadcast_reach=0.80,
        digital_media_presence=0.70,
        tourism_attractiveness=0.80,
        cultural_significance=0.85,
        international_accessibility=0.75,
        
        # Organizational Experience data (good)
        international_events=[(0.7, 0.80), (0.6, 0.75)],
        management_qualification=0.75,
        communication_service=0.70,
        local_authority_partnership=0.80,
        sports_federation_partnership=0.75
    )
    teams.append(al_ahly)
    

    return teams


def main():
    # Create sample teams
    teams = create_sample_teams()
    
    # Initialize selector with teams
    selector = GSLTeamSelector(teams)
    
    # Get scores table
    scores_df = selector.get_team_scores_df()
    print("Team Scores:")
    print(scores_df)
    
    # Select 20 teams
    selected_teams = selector.select_teams(num_teams=20)
    
    # Print selection results
    print("\nSelected Teams:")
    for i, team in enumerate(selected_teams, 1):
        print(f"{i}. {team.name} ({team.continent}) - Score: {selector.team_scores[team.id]:.4f}")
    
    # Print continent distribution
    print("\nContinent Distribution:")
    for continent, count in selector.continent_counts.items():
        print(f"{continent}: {count} teams")


if __name__ == "__main__":
    main()

def create_all_teams():
    """Create data for all 31 teams (24 selected + 7 additional)"""
    teams = []
    
    # ----- NORTH AMERICA (5) -----
    
    # Boston Celtics (USA)
    boston_celtics = Team(
        id="BOS", 
        name="Boston Celtics", 
        continent="North America", 
        region="USA East",
        
        # Sporting Level data (NBA powerhouse)
        national_rankings=[0.95, 1.0, 0.85, 0.80, 0.75],  # Recent NBA Finals appearance
        continental_participations=[
            {"NBA": 0.95}, {"NBA": 1.0}, {"NBA": 0.85}, 
            {"NBA": 0.80}, {"NBA": 0.75}
        ],
        international_ranking=2,
        
        # Infrastructure data (excellent)
        arena_capacity=19580,  # TD Garden
        arena_modernity=0.90,
        training_facilities=0.95,  # Auerbach Center
        auxiliary_platforms=0.92,
        airport_accessibility=0.95,  # Logan International
        railway_accessibility=0.90,
        other_transport=0.85,
        
        # Financial Stability data (excellent)
        budget=20000000,
        required_budget=10000000,
        sponsorship_strength=0.95,
        media_partnership=0.95,
        financial_fair_play=[0.95, 0.95, 0.95, 0.90, 0.90],
        
        # Marketing Potential data (global brand)
        social_media_following=18500000,
        average_attendance=18200,
        regional_market_size=0.95,
        tv_broadcast_reach=0.98,
        digital_media_presence=0.95,
        tourism_attractiveness=0.90,
        cultural_significance=0.95,  # Historic franchise
        international_accessibility=0.95,
        
        # Organizational Experience data (top-tier)
        international_events=[(0.9, 0.95), (0.9, 0.95), (0.8, 0.90)],
        management_qualification=0.95,
        communication_service=0.95,
        local_authority_partnership=0.90,
        sports_federation_partnership=0.95
    )
    teams.append(boston_celtics)
    
    # Los Angeles Lakers (USA)
    la_lakers = Team(
        id="LAL", 
        name="Los Angeles Lakers", 
        continent="North America", 
        region="USA West",
        
        # Sporting Level data (NBA royalty)
        national_rankings=[0.85, 1.0, 0.95, 0.70, 0.60],  # Recent championship
        continental_participations=[
            {"NBA": 0.85}, {"NBA": 1.0}, {"NBA": 0.95}, 
            {"NBA": 0.70}, {"NBA": 0.60}
        ],
        international_ranking=1,
        
        # Infrastructure data (excellent)
        arena_capacity=19000,  # Crypto.com Arena
        arena_modernity=0.95,
        training_facilities=0.95,  # UCLA Health Training Center
        auxiliary_platforms=0.92,
        airport_accessibility=0.95,  # LAX
        railway_accessibility=0.75,
        other_transport=0.80,
        
        # Financial Stability data (excellent)
        budget=20000000,
        required_budget=10000000,
        sponsorship_strength=1.0,
        media_partnership=1.0,  # Lakers have exceptional media deals
        financial_fair_play=[0.95, 0.95, 0.95, 0.90, 0.90],
        
        # Marketing Potential data (global icon)
        social_media_following=20000000,
        average_attendance=18700,
        regional_market_size=1.0,  # LA market
        tv_broadcast_reach=1.0,
        digital_media_presence=1.0,
        tourism_attractiveness=0.95,
        cultural_significance=1.0,  # Most famous basketball team globally
        international_accessibility=0.95,
        
        # Organizational Experience data (top-tier)
        international_events=[(1.0, 0.95), (0.9, 0.95), (0.9, 0.95)],
        management_qualification=0.90,
        communication_service=0.95,
        local_authority_partnership=0.90,
        sports_federation_partnership=0.95
    )
    teams.append(la_lakers)
    
    # Milwaukee Bucks (USA)
    milwaukee_bucks = Team(
        id="MIL", 
        name="Milwaukee Bucks", 
        continent="North America", 
        region="USA Midwest",
        
        # Sporting Level data (Recent NBA champion)
        national_rankings=[0.90, 0.85, 1.0, 0.90, 0.80],
        continental_participations=[
            {"NBA": 0.90}, {"NBA": 0.85}, {"NBA": 1.0}, 
            {"NBA": 0.90}, {"NBA": 0.80}
        ],
        international_ranking=5,
        
        # Infrastructure data (excellent)
        arena_capacity=17500,  # Fiserv Forum
        arena_modernity=0.95,  # New arena
        training_facilities=0.90,
        auxiliary_platforms=0.85,
        airport_accessibility=0.85,
        railway_accessibility=0.80,
        other_transport=0.75,
        
        # Financial Stability data (very good)
        budget=18000000,
        required_budget=10000000,
        sponsorship_strength=0.85,
        media_partnership=0.85,
        financial_fair_play=[0.95, 0.95, 0.90, 0.90, 0.85],
        
        # Marketing Potential data (growing global brand)
        social_media_following=14000000,
        average_attendance=17200,
        regional_market_size=0.75,  # Smaller market
        tv_broadcast_reach=0.85,
        digital_media_presence=0.90,
        tourism_attractiveness=0.75,
        cultural_significance=0.85,
        international_accessibility=0.80,
        
        # Organizational Experience data (very good)
        international_events=[(0.8, 0.90), (0.8, 0.85), (0.7, 0.85)],
        management_qualification=0.90,
        communication_service=0.85,
        local_authority_partnership=0.90,
        sports_federation_partnership=0.85
    )
    teams.append(milwaukee_bucks)
    
    # Toronto Raptors (Canada)
    toronto_raptors = Team(
        id="TOR", 
        name="Toronto Raptors", 
        continent="North America", 
        region="Canada",
        
        # Sporting Level data (recent NBA champion)
        national_rankings=[0.80, 0.75, 0.85, 1.0, 0.80],
        continental_participations=[
            {"NBA": 0.80}, {"NBA": 0.75}, {"NBA": 0.85}, 
            {"NBA": 1.0}, {"NBA": 0.80}
        ],
        international_ranking=8,
        
        # Infrastructure data (excellent)
        arena_capacity=19800,  # Scotiabank Arena
        arena_modernity=0.90,
        training_facilities=0.90,
        auxiliary_platforms=0.85,
        airport_accessibility=0.90,  # Toronto Pearson
        railway_accessibility=0.90,
        other_transport=0.85,
        
        # Financial Stability data (very good)
        budget=17000000,
        required_budget=10000000,
        sponsorship_strength=0.90,
        media_partnership=0.90,
        financial_fair_play=[0.90, 0.90, 0.90, 0.85, 0.85],
        
        # Marketing Potential data (international appeal)
        social_media_following=15000000,
        average_attendance=19200,
        regional_market_size=0.90,  # Major Canadian market
        tv_broadcast_reach=0.90,
        digital_media_presence=0.90,
        tourism_attractiveness=0.90,
        cultural_significance=0.90,  # Canada's team
        international_accessibility=0.90,
        
        # Organizational Experience data (excellent)
        international_events=[(0.9, 0.90), (0.8, 0.90), (0.8, 0.85)],
        management_qualification=0.90,
        communication_service=0.90,
        local_authority_partnership=0.90,
        sports_federation_partnership=0.85
    )
    teams.append(toronto_raptors)
    
    # Capitanes de Ciudad de México (Mexico)
    capitanes_mexico = Team(
        id="MEX", 
        name="Capitanes de Ciudad de México", 
        continent="North America", 
        region="Mexico",
        
        # Sporting Level data (G League team, developing)
        national_rankings=[0.90, 0.85, 0.90, 0.80, 0.75],  # Strong in Mexican league
        continental_participations=[
            {"G League": 0.70}, {"G League": 0.65}, {"FIBA Americas": 0.60}, 
            {"FIBA Americas": 0.60}, {"FIBA Americas": 0.55}
        ],
        international_ranking=55,
        
        # Infrastructure data (good but not elite)
        arena_capacity=22300,  # Arena Ciudad de Mexico
        arena_modernity=0.75,
        training_facilities=0.70,
        auxiliary_platforms=0.65,
        airport_accessibility=0.85,  # Mexico City International
        railway_accessibility=0.70,
        other_transport=0.75,
        
        # Financial Stability data (solid)
        budget=10000000,
        required_budget=8000000,
        sponsorship_strength=0.75,
        media_partnership=0.80,
        financial_fair_play=[0.85, 0.80, 0.80, 0.75, 0.75],
        
        # Marketing Potential data (strong regional appeal)
        social_media_following=4500000,
        average_attendance=10000,
        regional_market_size=0.85,  # Huge Mexico City market
        tv_broadcast_reach=0.80,
        digital_media_presence=0.75,
        tourism_attractiveness=0.90,
        cultural_significance=0.85,  # Growing basketball culture
        international_accessibility=0.85,
        
        # Organizational Experience data (developing)
        international_events=[(0.7, 0.75), (0.6, 0.70), (0.5, 0.70)],
        management_qualification=0.75,
        communication_service=0.75,
        local_authority_partnership=0.80,
        sports_federation_partnership=0.75
    )
    teams.append(capitanes_mexico)
    
    # ----- EUROPE (5) -----
    
    # Real Madrid (Spain)
    real_madrid = Team(
        id="RMA", 
        name="Real Madrid", 
        continent="Europe", 
        region="Western Europe",
        
        # Sporting Level data (Euroleague powerhouse)
        national_rankings=[1.0, 0.95, 1.0, 0.95, 1.0],  # Dominant in ACB League
        continental_participations=[
            {"Euroleague": 0.95}, {"Euroleague": 0.90}, {"Euroleague": 1.0}, 
            {"Euroleague": 0.95}, {"Euroleague": 0.90}
        ],
        international_ranking=3,
        
        # Infrastructure data (excellent)
        arena_capacity=15000,  # WiZink Center
        arena_modernity=0.90,
        training_facilities=0.95,
        auxiliary_platforms=0.90,
        airport_accessibility=0.95,  # Madrid Barajas
        railway_accessibility=0.95,
        other_transport=0.90,
        
        # Financial Stability data (exceptional)
        budget=19000000,
        required_budget=10000000,
        sponsorship_strength=0.95,
        media_partnership=0.95,
        financial_fair_play=[0.95, 0.95, 0.90, 0.90, 0.90],
        
        # Marketing Potential data (global brand)
        social_media_following=17000000,
        average_attendance=12000,
        regional_market_size=0.95,
        tv_broadcast_reach=0.95,
        digital_media_presence=0.95,
        tourism_attractiveness=0.95,
        cultural_significance=0.95,  # Part of iconic sports club
        international_accessibility=0.95,
        
        # Organizational Experience data (top-tier)
        international_events=[(0.9, 0.95), (0.9, 0.90), (0.9, 0.95)],
        management_qualification=0.95,
        communication_service=0.95,
        local_authority_partnership=0.90,
        sports_federation_partnership=0.95
    )
    teams.append(real_madrid)
    
    # Anadolu Efes (Turkey)
    anadolu_efes = Team(
        id="ANE", 
        name="Anadolu Efes", 
        continent="Europe", 
        region="Eastern Europe",
        
        # Sporting Level data (Euroleague champion)
        national_rankings=[1.0, 0.95, 1.0, 0.95, 0.90],
        continental_participations=[
            {"Euroleague": 1.0}, {"Euroleague": 0.95}, {"Euroleague": 0.85}, 
            {"Euroleague": 0.80}, {"Euroleague": 0.75}
        ],
        international_ranking=4,
        
        # Infrastructure data (very good)
        arena_capacity=16000,  # Sinan Erdem Dome
        arena_modernity=0.85,
        training_facilities=0.85,
        auxiliary_platforms=0.80,
        airport_accessibility=0.90,  # Istanbul Airport
        railway_accessibility=0.85,
        other_transport=0.80,
        
        # Financial Stability data (very good)
        budget=16000000,
        required_budget=10000000,
        sponsorship_strength=0.90,
        media_partnership=0.85,
        financial_fair_play=[0.90, 0.90, 0.85, 0.85, 0.80],
        
        # Marketing Potential data (strong continental brand)
        social_media_following=10000000,
        average_attendance=12000,
        regional_market_size=0.90,
        tv_broadcast_reach=0.85,
        digital_media_presence=0.85,
        tourism_attractiveness=0.90,  # Istanbul
        cultural_significance=0.85,
        international_accessibility=0.90,
        
        # Organizational Experience data (excellent)
        international_events=[(0.9, 0.90), (0.8, 0.85), (0.8, 0.80)],
        management_qualification=0.90,
        communication_service=0.85,
        local_authority_partnership=0.85,
        sports_federation_partnership=0.90
    )
    teams.append(anadolu_efes)
    
    # Panathinaikos OPAP (Greece)
    panathinaikos = Team(
        id="PAO", 
        name="Panathinaikos OPAP", 
        continent="Europe", 
        region="Southern Europe",
        
        # Sporting Level data (Euroleague traditional power)
        national_rankings=[1.0, 0.95, 1.0, 1.0, 0.95],
        continental_participations=[
            {"Euroleague": 0.85}, {"Euroleague": 0.80}, {"Euroleague": 0.85}, 
            {"Euroleague": 0.90}, {"Euroleague": 0.95}
        ],
        international_ranking=12,
        
        # Infrastructure data (very good)
        arena_capacity=18000,  # OAKA Olympic Arena
        arena_modernity=0.80,
        training_facilities=0.85,
        auxiliary_platforms=0.80,
        airport_accessibility=0.85,  # Athens International
        railway_accessibility=0.80,
        other_transport=0.75,
        
        # Financial Stability data (good)
        budget=14000000,
        required_budget=10000000,
        sponsorship_strength=0.85,
        media_partnership=0.80,
        financial_fair_play=[0.85, 0.85, 0.80, 0.80, 0.75],
        
        # Marketing Potential data (strong regional appeal)
        social_media_following=7000000,
        average_attendance=10000,
        regional_market_size=0.80,
        tv_broadcast_reach=0.80,
        digital_media_presence=0.80,
        tourism_attractiveness=0.85,  # Athens
        cultural_significance=0.85,
        international_accessibility=0.85,
        
        # Organizational Experience data (very good)
        international_events=[(0.8, 0.85), (0.8, 0.80), (0.7, 0.80)],
        management_qualification=0.85,
        communication_service=0.80,
        local_authority_partnership=0.85,
        sports_federation_partnership=0.85
    )
    teams.append(panathinaikos)
    
    # CSKA Moscow (Russia)
    cska_moscow = Team(
        id="CSK", 
        name="CSKA Moscow", 
        continent="Europe", 
        region="Eastern Europe",
        
        # Sporting Level data (Euroleague powerhouse)
        national_rankings=[1.0, 1.0, 1.0, 1.0, 0.95],  # Dominant domestically
        continental_participations=[
            {"Euroleague": 0.90}, {"Euroleague": 0.95}, {"Euroleague": 1.0}, 
            {"Euroleague": 0.90}, {"Euroleague": 0.95}
        ],
        international_ranking=6,
        
        # Infrastructure data (excellent)
        arena_capacity=14000,  # Megasport Arena
        arena_modernity=0.85,
        training_facilities=0.90,
        auxiliary_platforms=0.85,
        airport_accessibility=0.90,  # Moscow airports
        railway_accessibility=0.90,
        other_transport=0.85,
        
        # Financial Stability data (very strong)
        budget=18000000,
        required_budget=10000000,
        sponsorship_strength=0.90,
        media_partnership=0.85,
        financial_fair_play=[0.90, 0.90, 0.85, 0.85, 0.80],
        
        # Marketing Potential data (strong continental brand)
        social_media_following=8000000,
        average_attendance=11000,
        regional_market_size=0.90,
        tv_broadcast_reach=0.85,
        digital_media_presence=0.80,
        tourism_attractiveness=0.85,
        cultural_significance=0.85,
        international_accessibility=0.80,  # Some visa challenges
        
        # Organizational Experience data (excellent)
        international_events=[(0.9, 0.90), (0.8, 0.90), (0.8, 0.85)],
        management_qualification=0.90,
        communication_service=0.85,
        local_authority_partnership=0.90,
        sports_federation_partnership=0.90
    )
    teams.append(cska_moscow)
    
    # Maccabi Tel Aviv (Israel)
    maccabi_tel_aviv = Team(
        id="MTA", 
        name="Maccabi Tel Aviv", 
        continent="Europe", 
        region="Eastern Mediterranean",
        
        # Sporting Level data (Euroleague traditional power)
        national_rankings=[1.0, 0.95, 1.0, 1.0, 0.95],  # Dominant in Israel
        continental_participations=[
            {"Euroleague": 0.80}, {"Euroleague": 0.75}, {"Euroleague": 0.85}, 
            {"Euroleague": 0.90}, {"Euroleague": 0.85}
        ],
        international_ranking=15,
        
        # Infrastructure data (very good)
        arena_capacity=11000,  # Menora Mivtachim Arena
        arena_modernity=0.85,
        training_facilities=0.85,
        auxiliary_platforms=0.80,
        airport_accessibility=0.90,  # Ben Gurion
        railway_accessibility=0.85,
        other_transport=0.80,
        
        # Financial Stability data (good)
        budget=13000000,
        required_budget=10000000,
        sponsorship_strength=0.85,
        media_partnership=0.80,
        financial_fair_play=[0.85, 0.85, 0.80, 0.80, 0.75],
        
        # Marketing Potential data (strong regional and Jewish diaspora appeal)
        social_media_following=5000000,
        average_attendance=9500,
        regional_market_size=0.75,
        tv_broadcast_reach=0.80,
        digital_media_presence=0.80,
        tourism_attractiveness=0.85,  # Tel Aviv
        cultural_significance=0.85,
        international_accessibility=0.80,
        
        # Organizational Experience data (very good)
        international_events=[(0.8, 0.85), (0.8, 0.80), (0.7, 0.80)],
        management_qualification=0.85,
        communication_service=0.85,
        local_authority_partnership=0.80,
        sports_federation_partnership=0.85
    )
    teams.append(maccabi_tel_aviv)
    
    # ----- ASIA (4, including one expansion team) -----
    
    # Guangdong Southern Tigers (China)
    guangdong_tigers = Team(
        id="GST", 
        name="Guangdong Southern Tigers", 
        continent="Asia", 
        region="East Asia",
        
        # Sporting Level data (CBA powerhouse)
        national_rankings=[1.0, 1.0, 0.95, 1.0, 0.95],  # Dominant in CBA
        continental_participations=[
            {"FIBA Asia Champions Cup": 0.90}, {"FIBA Asia Champions Cup": 0.85}, 
            {"FIBA Asia Champions Cup": 0.90}, {"FIBA Asia Champions Cup": 0.85}, 
            {"FIBA Asia Champions Cup": 0.80}
        ],
        international_ranking=25,
        
        # Infrastructure data (excellent for Asia)
        arena_capacity=16000,  # Dongguan Basketball Center
        arena_modernity=0.90,
        training_facilities=0.85,
        auxiliary_platforms=0.80,
        airport_accessibility=0.90,  # Guangzhou airports
        railway_accessibility=0.95,  # Chinese high-speed rail
        other_transport=0.85,
        
        # Financial Stability data (very strong)
        budget=15000000,
        required_budget=10000000,
        sponsorship_strength=0.90,
        media_partnership=0.85,
        financial_fair_play=[0.90, 0.85, 0.85, 0.80, 0.80],
        
        # Marketing Potential data (massive domestic market)
        social_media_following=12000000,
        average_attendance=12000,
        regional_market_size=0.95,  # Huge Chinese market
        tv_broadcast_reach=0.95,
        digital_media_presence=0.90,
        tourism_attractiveness=0.80,
        cultural_significance=0.85,
        international_accessibility=0.75,  # Visa/travel challenges
        
        # Organizational Experience data (strong)
        international_events=[(0.8, 0.85), (0.7, 0.80), (0.7, 0.75)],
        management_qualification=0.85,
        communication_service=0.80,
        local_authority_partnership=0.90,
        sports_federation_partnership=0.85
    )
    teams.append(guangdong_tigers)
    
    # Alvark Tokyo (Japan)
    alvark_tokyo = Team(
        id="ALT", 
        name="Alvark Tokyo", 
        continent="Asia", 
        region="East Asia",
        
        # Sporting Level data (B.League Champion)
        national_rankings=[0.95, 1.0, 0.95, 0.90, 0.85],
        continental_participations=[
            {"FIBA Asia Champions Cup": 0.85}, {"FIBA Asia Champions Cup": 0.80}, 
            {"FIBA Asia Champions Cup": 0.75}, {"FIBA Asia Champions Cup": 0.70}, 
            {"FIBA Asia Champions Cup": 0.70}
        ],
        international_ranking=35,
        
        # Infrastructure data (very good)
        arena_capacity=10000,  # Arena Tachikawa Tachihi
        arena_modernity=0.85,
        training_facilities=0.85,
        auxiliary_platforms=0.80,
        airport_accessibility=0.95,  # Tokyo airports
        railway_accessibility=0.95,  # Japanese rail system
        other_transport=0.90,
        
        # Financial Stability data (strong)
        budget=12000000,
        required_budget=10000000,
        sponsorship_strength=0.85,
        media_partnership=0.80,
        financial_fair_play=[0.90, 0.90, 0.85, 0.85, 0.80],
        
        # Marketing Potential data (strong in Japan)
        social_media_following=3500000,
        average_attendance=8000,
        regional_market_size=0.90,  # Tokyo market
        tv_broadcast_reach=0.85,
        digital_media_presence=0.85,
        tourism_attractiveness=0.95,  # Tokyo
        cultural_significance=0.80,
        international_accessibility=0.90,
        
        # Organizational Experience data (good)
        international_events=[(0.7, 0.85), (0.7, 0.80), (0.6, 0.80)],
        management_qualification=0.85,
        communication_service=0.90,
        local_authority_partnership=0.85,
        sports_federation_partnership=0.80
    )
    teams.append(alvark_tokyo)
    
    # Seoul SK Knights (South Korea)
    seoul_knights = Team(
        id="SSK", 
        name="Seoul SK Knights", 
        continent="Asia", 
        region="East Asia",
        
        # Sporting Level data (KBL Champion)
        national_rankings=[1.0, 0.90, 0.85, 0.80, 0.75],
        continental_participations=[
            {"FIBA Asia Champions Cup": 0.80}, {"FIBA Asia Champions Cup": 0.75}, 
            {"FIBA Asia Champions Cup": 0.70}, {"FIBA Asia Champions Cup": 0.65}, 
            {"FIBA Asia Champions Cup": 0.65}
        ],
        international_ranking=45,
        
        # Infrastructure data (good)
        arena_capacity=8000,  # Jamsil Arena
        arena_modernity=0.80,
        training_facilities=0.80,
        auxiliary_platforms=0.75,
        airport_accessibility=0.90,  # Incheon International
        railway_accessibility=0.90,
        other_transport=0.85,
        
        # Financial Stability data (good)
        budget=11000000,
        required_budget=10000000,
        sponsorship_strength=0.80,  # SK Group backing
        media_partnership=0.75,
        financial_fair_play=[0.85, 0.85, 0.80, 0.80, 0.75],
        
        # Marketing Potential data (strong in Korea)
        social_media_following=2500000,
        average_attendance=7000,
        regional_market_size=0.85,  # Seoul market
        tv_broadcast_reach=0.80,
        digital_media_presence=0.85,  # Strong in tech-savvy Korea
        tourism_attractiveness=0.85,  # Seoul
        cultural_significance=0.75,
        international_accessibility=0.85,
        
        # Organizational Experience data (moderate)
        international_events=[(0.7, 0.75), (0.6, 0.75), (0.6, 0.70)],
        management_qualification=0.80,
        communication_service=0.80,
        local_authority_partnership=0.85,
        sports_federation_partnership=0.75
    )
    teams.append(seoul_knights)
    
    # Barangay Ginebra San Miguel (Philippines) - Expansion Team
    barangay_ginebra = Team(
        id="BGS", 
        name="Barangay Ginebra San Miguel", 
        continent="Asia", 
        region="Southeast Asia",
        
        # Sporting Level data (PBA powerhouse)
        national_rankings=[1.0, 0.95, 1.0, 0.90, 0.95],  # Dominant in PBA
        continental_participations=[
            {"FIBA Asia Champions Cup": 0.75}, {"FIBA Asia Champions Cup": 0.70}, 
            {"East Asia Super League": 0.75}, {"East Asia Super League": 0.70}, 
            {"East Asia Super League": 0.65}
        ],
        international_ranking=50,
        
        # Infrastructure data (adequate)
        arena_capacity=15000,  # Smart Araneta Coliseum (shared)
        arena_modernity=0.75,
        training_facilities=0.75,
        auxiliary_platforms=0.70,
        airport_accessibility=0.80,  # Manila airports
        railway_accessibility=0.70,
        other_transport=0.65,
        
        # Financial Stability data (good, corporate backed)
        budget=10000000,
        required_budget=9000000,
        sponsorship_strength=0.85,  # San Miguel Corporation backing
        media_partnership=0.80,
        financial_fair_play=[0.85, 0.80, 0.80, 0.75, 0.75],
        
        # Marketing Potential data (phenomenal in Philippines)
        social_media_following=8000000,
        average_attendance=14000,  # Exceptional attendance
        regional_market_size=0.85,  # Philippines basketball obsession
        tv_broadcast_reach=0.85,
        digital_media_presence=0.85,
        tourism_attractiveness=0.75,
        cultural_significance=0.90,  # Cultural icon in Philippines
        international_accessibility=0.75,
        
        # Organizational Experience data (moderate)
        international_events=[(0.7, 0.75), (0.6, 0.70), (0.5, 0.70)],
        management_qualification=0.80,
        communication_service=0.75,
        local_authority_partnership=0.80,
        sports_federation_partnership=0.80
    )
    teams.append(barangay_ginebra)
    
    # Al Riyadi Beirut (Lebanon) - Expansion Team
    al_riyadi = Team(
        id="ARB", 
        name="Al Riyadi Club Beirut", 
        continent="Asia", 
        region="West Asia",
        
        # Sporting Level data (Lebanese/Arab champion)
        national_rankings=[1.0, 1.0, 0.95, 1.0, 0.95],  # Dominant in Lebanon
        continental_participations=[
            {"FIBA Asia Champions Cup": 0.90}, {"FIBA Asia Champions Cup": 0.85}, 
            {"West Asia Super League": 0.90}, {"West Asia Super League": 0.85}, 
            {"West Asia Super League": 0.80}
        ],
        international_ranking=60,
        
        # Infrastructure data (good)
        arena_capacity=8000,  # Manara Stadium
        arena_modernity=0.70,
        training_facilities=0.75,
        auxiliary_platforms=0.65,
        airport_accessibility=0.80,  # Beirut International
        railway_accessibility=0.60,
        other_transport=0.70,
        
        # Financial Stability data (moderate to good)
        budget=9500000,
        required_budget=9000000,
        sponsorship_strength=0.75,
        media_partnership=0.70,
        financial_fair_play=[0.80, 0.80, 0.75, 0.75, 0.70],
        
        # Marketing Potential data (strong regional appeal)
        social_media_following=3500000,
        average_attendance=7500,
        regional_market_size=0.75,  # Arab world reach
        tv_broadcast_reach=0.75,
        digital_media_presence=0.70,
        tourism_attractiveness=0.75,  # Beirut
        cultural_significance=0.80,  # Basketball importance in Lebanon
        international_accessibility=0.65,  # Some travel challenges
        
        # Organizational Experience data (good regional experience)
        international_events=[(0.8, 0.75), (0.7, 0.75), (0.7, 0.70)],
        management_qualification=0.75,
        communication_service=0.70,
        local_authority_partnership=0.75,
        sports_federation_partnership=0.80
    )
    teams.append(al_riyadi)
    
    # ----- SOUTH AMERICA (4, including one expansion team) -----
    
    # Flamengo (Brazil)
    flamengo = Team(
        id="FLA", 
        name="Flamengo", 
        continent="South America", 
        region="Brazil",
        
        # Sporting Level data (Brazilian NBB champion)
        national_rankings=[1.0, 0.95, 1.0, 0.90, 0.85],
        continental_participations=[
            {"FIBA Americas League": 0.85}, {"FIBA Americas League": 0.80}, 
            {"FIBA Americas League": 0.85}, {"FIBA Americas League": 0.80}, 
            {"FIBA Americas League": 0.75}
        ],
        international_ranking=40,
        
        # Infrastructure data (good)
        arena_capacity=10000,  # Maracanãzinho Gymnasium
        arena_modernity=0.75,
        training_facilities=0.80,
        auxiliary_platforms=0.75,
        airport_accessibility=0.85,  # Rio de Janeiro airports
        railway_accessibility=0.70,
        other_transport=0.75,
        
        # Financial Stability data (strong for South America)
        budget=12000000,
        required_budget=9000000,
        sponsorship_strength=0.85,  # Major sports club
        media_partnership=0.85,
        financial_fair_play=[0.85, 0.80, 0.80, 0.75, 0.75],
        
        # Marketing Potential data (massive following from football club)
        social_media_following=14000000,  # Leveraging football fanbase
        average_attendance=8500,
        regional_market_size=0.90,  # Huge Brazilian market
        tv_broadcast_reach=0.85,
        digital_media_presence=0.80,
        tourism_attractiveness=0.90,  # Rio de Janeiro
        cultural_significance=0.85,  # Major sports institution
        international_accessibility=0.80,
        
        # Organizational Experience data (good)
        international_events=[(0.8, 0.80), (0.7, 0.75), (0.6, 0.75)],
        management_qualification=0.80,
        communication_service=0.75,
        local_authority_partnership=0.80,
        sports_federation_partnership=0.80
    )
    teams.append(flamengo)
    
    # San Lorenzo (Argentina)
    san_lorenzo = Team(
        id="SLA", 
        name="San Lorenzo", 
        continent="South America", 
        region="Southern Cone",
        
        # Sporting Level data (Argentine Liga Nacional champion)
        national_rankings=[1.0, 0.95, 1.0, 0.90, 0.85],
        continental_participations=[
            {"FIBA Americas League": 0.90}, {"FIBA Americas League": 0.85}, 
            {"FIBA Americas League": 0.90}, {"FIBA Americas League": 0.80}, 
            {"FIBA Americas League": 0.75}
        ],
        international_ranking=38,
        
        # Infrastructure data (adequate)
        arena_capacity=7500,  # Roberto Pando Sports Center
        arena_modernity=0.70,
        training_facilities=0.75,
        auxiliary_platforms=0.70,
        airport_accessibility=0.85,  # Buenos Aires airports
        railway_accessibility=0.75,
        other_transport=0.70,
        
        # Financial Stability data (good for region)
        budget=10000000,
        required_budget=9000000,
        sponsorship_strength=0.80,
        media_partnership=0.75,
        financial_fair_play=[0.80, 0.80, 0.75, 0.75, 0.70],
        
        # Marketing Potential data (good regional appeal)
        social_media_following=7000000,  # Leveraging football club fame
        average_attendance=7000,
        regional_market_size=0.80,  # Buenos Aires market
        tv_broadcast_reach=0.75,
        digital_media_presence=0.75,
        tourism_attractiveness=0.85,  # Buenos Aires
        cultural_significance=0.80,
        international_accessibility=0.75,
        
        # Organizational Experience data (moderate)
        international_events=[(0.7, 0.75), (0.7, 0.70), (0.6, 0.70)],
        management_qualification=0.75,
        communication_service=0.70,
        local_authority_partnership=0.75,
        sports_federation_partnership=0.75
    )
    teams.append(san_lorenzo)
    
    # Nacional (Uruguay)
    nacional = Team(
        id="NAC", 
        name="Nacional", 
        continent="South America", 
        region="Southern Cone",
        
        # Sporting Level data (Uruguayan champion)
        national_rankings=[1.0, 0.95, 0.90, 1.0, 0.95],
        continental_participations=[
            {"FIBA Americas League": 0.70}, {"FIBA Americas League": 0.65}, 
            {"FIBA Americas League": 0.70}, {"FIBA Americas League": 0.65}, 
            {"FIBA Americas League": 0.60}
        ],
        international_ranking=65,
        
        # Infrastructure data (adequate)
        arena_capacity=6000,
        arena_modernity=0.65,
        training_facilities=0.70,
        auxiliary_platforms=0.65,
        airport_accessibility=0.80,  # Montevideo
        railway_accessibility=0.65,
        other_transport=0.65,
        
        # Financial Stability data (moderate)
        budget=9000000,
        required_budget=8500000,
        sponsorship_strength=0.70,
        media_partnership=0.65,
        financial_fair_play=[0.80, 0.75, 0.75, 0.70, 0.70],
        
        # Marketing Potential data (moderate)
        social_media_following=3000000,  # Leveraging football club
        average_attendance=5500,
        regional_market_size=0.65,  # Smaller Uruguayan market
        tv_broadcast_reach=0.65,
        digital_media_presence=0.70,
        tourism_attractiveness=0.80,  # Montevideo
        cultural_significance=0.75,
        international_accessibility=0.70,
        
        # Organizational Experience data (moderate)
        international_events=[(0.6, 0.70), (0.6, 0.65), (0.5, 0.65)],
        management_qualification=0.70,
        communication_service=0.65,
        local_authority_partnership=0.75,
        sports_federation_partnership=0.70
    )
    teams.append(nacional)
    
    # Franca Basquetebol Clube (Brazil) - Expansion Team
    franca = Team(
        id="FBC", 
        name="Franca Basquetebol Clube", 
        continent="South America", 
        region="Brazil",
        
        # Sporting Level data (Brazilian NBB top team)
        national_rankings=[0.95, 1.0, 0.90, 0.85, 0.80],
        continental_participations=[
            {"FIBA Americas League": 0.85}, {"FIBA Americas League": 0.90}, 
            {"FIBA Americas League": 0.80}, {"FIBA Americas League": 0.75}, 
            {"FIBA Americas League": 0.70}
        ],
        international_ranking=55,
        
        # Infrastructure data (adequate)
        arena_capacity=9000,  # Pedrocão Arena
        arena_modernity=0.75,
        training_facilities=0.75,
        auxiliary_platforms=0.70,
        airport_accessibility=0.75,  # Regional airport
        railway_accessibility=0.65,
        other_transport=0.70,
        
        # Financial Stability data (moderate)
        budget=9500000,
        required_budget=9000000,
        sponsorship_strength=0.75,
        media_partnership=0.70,
        financial_fair_play=[0.80, 0.80, 0.75, 0.75, 0.70],
        
        # Marketing Potential data (strong basketball culture)
        social_media_following=2000000,
        average_attendance=8000,  # Strong local basketball following
        regional_market_size=0.70,  # Smaller Brazilian city but basketball hotbed
        tv_broadcast_reach=0.70,
        digital_media_presence=0.75,
        tourism_attractiveness=0.65,
        cultural_significance=0.85,  # "Brazilian Basketball Capital"
        international_accessibility=0.65,
        
        # Organizational Experience data (moderate)
        international_events=[(0.7, 0.75), (0.7, 0.70), (0.6, 0.70)],
        management_qualification=0.80,  # Basketball-focused management
        communication_service=0.75,
        local_authority_partnership=0.80,
        sports_federation_partnership=0.75
    )
    teams.append(franca)
    
    # ----- OCEANIA (2) -----
    
    # Sydney Kings (Australia)
    sydney_kings = Team(
        id="SDK", 
        name="Sydney Kings", 
        continent="Oceania", 
        region="Australia",
        
        # Sporting Level data (NBL champion)
        national_rankings=[1.0, 0.90, 0.95, 0.85, 0.80],
        continental_participations=[
            {"NBL": 1.0}, {"NBL": 0.90}, {"NBL": 0.95}, 
            {"NBL": 0.85}, {"NBL": 0.80}
        ],
        international_ranking=28,
        
        # Infrastructure data (very good)
        arena_capacity=11500,  # Qudos Bank Arena
        arena_modernity=0.85,
        training_facilities=0.85,
        auxiliary_platforms=0.80,
        airport_accessibility=0.90,  # Sydney Airport
        railway_accessibility=0.85,
        other_transport=0.85,
        
        # Financial Stability data (strong)
        budget=12000000,
        required_budget=9000000,
        sponsorship_strength=0.85,
        media_partnership=0.80,
        financial_fair_play=[0.90, 0.85, 0.85, 0.80, 0.80],
        
        # Marketing Potential data (strong in Australia)
        social_media_following=2500000,
        average_attendance=9500,
        regional_market_size=0.85,  # Sydney market
        tv_broadcast_reach=0.80,
        digital_media_presence=0.85,
        tourism_attractiveness=0.90,  # Sydney
        cultural_significance=0.80,
        international_accessibility=0.80,  # Distance challenges
        
        # Organizational Experience data (good)
        international_events=[(0.7, 0.85), (0.7, 0.80), (0.6, 0.80)],
        management_qualification=0.85,
        communication_service=0.85,
        local_authority_partnership=0.80,
        sports_federation_partnership=0.80
    )
    teams.append(sydney_kings)
    
    # New Zealand Breakers (New Zealand)
    nz_breakers = Team(
        id="NZB", 
        name="New Zealand Breakers", 
        continent="Oceania", 
        region="New Zealand",
        
        # Sporting Level data (NBL participant)
        national_rankings=[0.85, 0.80, 0.85, 0.90, 1.0],  # Past champion
        continental_participations=[
            {"NBL": 0.85}, {"NBL": 0.80}, {"NBL": 0.85}, 
            {"NBL": 0.90}, {"NBL": 1.0}
        ],
        international_ranking=40,
        
        # Infrastructure data (good)
        arena_capacity=9500,  # Spark Arena
        arena_modernity=0.80,
        training_facilities=0.80,
        auxiliary_platforms=0.75,
        airport_accessibility=0.85,  # Auckland Airport
        railway_accessibility=0.75,
        other_transport=0.80,
        
        # Financial Stability data (good)
        budget=10000000,
        required_budget=9000000,
        sponsorship_strength=0.80,
        media_partnership=0.75,
        financial_fair_play=[0.85, 0.85, 0.80, 0.80, 0.75],
        
        # Marketing Potential data (good in New Zealand)
        social_media_following=1500000,
        average_attendance=7500,
        regional_market_size=0.75,  # New Zealand market
        tv_broadcast_reach=0.75,
        digital_media_presence=0.80,
        tourism_attractiveness=0.90,  # Auckland/New Zealand
        cultural_significance=0.85,  # Basketball growing in rugby country
        international_accessibility=0.70,  # Distance challenges
        
        # Organizational Experience data (moderate)
        international_events=[(0.7, 0.75), (0.6, 0.75), (0.6, 0.70)],
        management_qualification=0.80,
        communication_service=0.80,
        local_authority_partnership=0.85,
        sports_federation_partnership=0.75
    )
    teams.append(nz_breakers)
    
    # ----- AFRICA (3, including one expansion team) -----
    
    # Al Ahly SC (Egypt)
    al_ahly = Team(
        id="AHL", 
        name="Al Ahly SC", 
        continent="Africa", 
        region="North Africa",
        
        # Sporting Level data (Egyptian champion)
        national_rankings=[1.0, 1.0, 0.95, 1.0, 0.95],
        continental_participations=[
            {"Basketball Africa League": 0.85}, {"Basketball Africa League": 0.80}, 
            {"Basketball Africa League": 0.75}, {"FIBA Africa Champions Cup": 0.80}, 
            {"FIBA Africa Champions Cup": 0.75}
        ],
        international_ranking=60,
        
        # Infrastructure data (good for region)
        arena_capacity=7500,
        arena_modernity=0.75,
        training_facilities=0.70,
        auxiliary_platforms=0.65,
        airport_accessibility=0.85,  # Cairo International
        railway_accessibility=0.75,
        other_transport=0.70,
        
        # Financial Stability data (good for region)
        budget=10000000,
        required_budget=9000000,
        sponsorship_strength=0.80,  # Major sports club
        media_partnership=0.75,
        financial_fair_play=[0.80, 0.80, 0.75, 0.75, 0.70],
        
        # Marketing Potential data (leveraging football club fame)
        social_media_following=12000000,  # Massive football following
        average_attendance=6500,
        regional_market_size=0.85,  # Major influence in MENA region
        tv_broadcast_reach=0.80,
        digital_media_presence=0.75,
        tourism_attractiveness=0.85,  # Cairo
        cultural_significance=0.90,  # Most successful African sports club
        international_accessibility=0.75,
        
        # Organizational Experience data (good)
        international_events=[(0.8, 0.75), (0.7, 0.75), (0.7, 0.70)],
        management_qualification=0.80,
        communication_service=0.75,
        local_authority_partnership=0.85,
        sports_federation_partnership=0.80
    )
    teams.append(al_ahly)
    
    # Petro de Luanda (Angola)
    petro_luanda = Team(
        id="PDL", 
        name="Petro de Luanda", 
        continent="Africa", 
        region="Southern Africa",
        
        # Sporting Level data (Angolan champion)
        national_rankings=[1.0, 0.95, 1.0, 0.95, 1.0],
        continental_participations=[
            {"Basketball Africa League": 0.90}, {"Basketball Africa League": 0.85}, 
            {"FIBA Africa Champions Cup": 0.85}, {"FIBA Africa Champions Cup": 0.80}, 
            {"FIBA Africa Champions Cup": 0.85}
        ],
        international_ranking=55,
        
        # Infrastructure data (adequate)
        arena_capacity=6000,  # Arena Pavilhão Multiusos do Kilamba
        arena_modernity=0.70,
        training_facilities=0.65,
        auxiliary_platforms=0.60,
        airport_accessibility=0.75,  # Luanda airport
        railway_accessibility=0.60,
        other_transport=0.65,
        
        # Financial Stability data (oil company backing)
        budget=9500000,
        required_budget=9000000,
        sponsorship_strength=0.80,  # State oil company backing
        media_partnership=0.70,
        financial_fair_play=[0.80, 0.75, 0.75, 0.70, 0.70],
        
        # Marketing Potential data (regional leader)
        social_media_following=1500000,
        average_attendance=5500,
        regional_market_size=0.75,  # Leader in Southern Africa basketball
        tv_broadcast_reach=0.70,
        digital_media_presence=0.65,
        tourism_attractiveness=0.65,
        cultural_significance=0.80,  # Basketball importance in Angola
        international_accessibility=0.60,  # Travel challenges
        
        # Organizational Experience data (growing)
        international_events=[(0.7, 0.70), (0.6, 0.70), (0.6, 0.65)],
        management_qualification=0.75,
        communication_service=0.65,
        local_authority_partnership=0.80,
        sports_federation_partnership=0.75
    )
    teams.append(petro_luanda)
    
    # US Monastir (Tunisia) - Expansion Team
    us_monastir = Team(
        id="USM", 
        name="US Monastir", 
        continent="Africa", 
        region="North Africa",
        
        # Sporting Level data (Tunisian champion, BAL champion)
        national_rankings=[1.0, 1.0, 0.95, 0.90, 0.85],
        continental_participations=[
            {"Basketball Africa League": 1.0}, {"Basketball Africa League": 0.90}, 
            {"Basketball Africa League": 0.85}, {"FIBA Africa Champions Cup": 0.80}, 
            {"FIBA Africa Champions Cup": 0.75}
        ],
        international_ranking=58,
        
        # Infrastructure data (adequate)
        arena_capacity=5500,  # Salle Omnisport de Monastir
        arena_modernity=0.65,
        training_facilities=0.70,
        auxiliary_platforms=0.60,
        airport_accessibility=0.75,  # Monastir Airport
        railway_accessibility=0.70,
        other_transport=0.65,
        
        # Financial Stability data (moderate)
        budget=9000000,
        required_budget=9000000,
        sponsorship_strength=0.70,
        media_partnership=0.65,
        financial_fair_play=[0.80, 0.75, 0.75, 0.70, 0.70],
        
        # Marketing Potential data (regional influence)
        social_media_following=1200000,
        average_attendance=5000,
        regional_market_size=0.70,  # North African influence
        tv_broadcast_reach=0.65,
        digital_media_presence=0.70,
        tourism_attractiveness=0.80,  # Monastir tourist area
        cultural_significance=0.75,
        international_accessibility=0.70,
        
        # Organizational Experience data (growing)
        international_events=[(0.8, 0.70), (0.7, 0.70), (0.6, 0.65)],
        management_qualification=0.75,
        communication_service=0.70,
        local_authority_partnership=0.75,
        sports_federation_partnership=0.70
    )
    teams.append(us_monastir)
    
    # ----- ADDITIONAL TEAMS (NOT SELECTED) -----
    
    # Besiktas (Turkey) - Not Selected
    besiktas = Team(
        id="BJK", 
        name="Besiktas", 
        continent="Europe", 
        region="Eastern Europe",
        
        # Sporting Level data (Turkish League, not dominant)
        national_rankings=[0.80, 0.75, 0.70, 0.80, 0.75],  # Not consistently top in Turkey
        continental_participations=[
            {"EuroCup": 0.70}, {"EuroCup": 0.65}, {"EuroCup": 0.70}, 
            {"EuroCup": 0.65}, {"EuroCup": 0.60}
        ],
        international_ranking=75,
        
        # Infrastructure data (decent)
        arena_capacity=6500,  # Akatlar Arena
        arena_modernity=0.70,
        training_facilities=0.70,
        auxiliary_platforms=0.65,
        airport_accessibility=0.90,  # Istanbul Airport
        railway_accessibility=0.85,
        other_transport=0.80,
        
        # Financial Stability data (moderate, football focus)
        budget=9000000,
        required_budget=9000000,
        sponsorship_strength=0.75,
        media_partnership=0.70,
        financial_fair_play=[0.75, 0.75, 0.70, 0.70, 0.65],
        
        # Marketing Potential data (leverages football brand)
        social_media_following=6000000,  # Football club followers
        average_attendance=5000,  # Modest for basketball
        regional_market_size=0.70,
        tv_broadcast_reach=0.75,
        digital_media_presence=0.75,
        tourism_attractiveness=0.90,  # Istanbul
        cultural_significance=0.75,
        international_accessibility=0.85,
        
        # Organizational Experience data (moderate)
        international_events=[(0.7, 0.70), (0.6, 0.70), (0.6, 0.65)],
        management_qualification=0.70,  # Football focus
        communication_service=0.75,
        local_authority_partnership=0.75,
        sports_federation_partnership=0.70
    )
    teams.append(besiktas)
    
    # Hapoel Jerusalem (Israel) - Not Selected
    hapoel_jerusalem = Team(
        id="HPJ", 
        name="Hapoel Jerusalem", 
        continent="Europe", 
        region="Eastern Mediterranean",
        
        # Sporting Level data (Israeli League)
        national_rankings=[0.90, 0.85, 0.90, 0.85, 0.80],  # Second tier in Israel
        continental_participations=[
            {"Basketball Champions League": 0.80}, {"Basketball Champions League": 0.75}, 
            {"Basketball Champions League": 0.70}, {"Basketball Champions League": 0.75}, 
            {"Basketball Champions League": 0.70}
        ],
        international_ranking=80,
        
        # Infrastructure data (good)
        arena_capacity=11600,  # Pais Arena
        arena_modernity=0.85,
        training_facilities=0.75,
        auxiliary_platforms=0.70,
        airport_accessibility=0.85,  # Ben Gurion (travel to Jerusalem)
        railway_accessibility=0.75,
        other_transport=0.70,
        
        # Financial Stability data (moderate)
        budget=8500000,
        required_budget=9000000,  # Just below requirement
        sponsorship_strength=0.75,
        media_partnership=0.70,
        financial_fair_play=[0.75, 0.75, 0.70, 0.70, 0.65],
        
        # Marketing Potential data (good local)
        social_media_following=1000000,
        average_attendance=8000,
        regional_market_size=0.65,
        tv_broadcast_reach=0.70,
        digital_media_presence=0.70,
        tourism_attractiveness=0.90,  # Jerusalem
        cultural_significance=0.75,
        international_accessibility=0.70,  # Security concerns
        
        # Organizational Experience data (moderate)
        international_events=[(0.7, 0.75), (0.6, 0.70), (0.6, 0.65)],
        management_qualification=0.75,
        communication_service=0.70,
        local_authority_partnership=0.70,
        sports_federation_partnership=0.65
    )
    teams.append(hapoel_jerusalem)
    
    # Basketball Club Wolves Vilnius (Lithuania) - Not Selected
    bc_wolves = Team(
        id="WLV", 
        name="BC Wolves Vilnius", 
        continent="Europe", 
        region="Northern Europe",
        
        # Sporting Level data (Lithuanian League)
        national_rankings=[0.85, 0.80, 0.75, 0.70, 0.65],  # Not dominant in Lithuania
        continental_participations=[
            {"Basketball Champions League": 0.70}, {"Basketball Champions League": 0.65}, 
            {"EuroCup": 0.70}, {"EuroCup": 0.65}, {"EuroCup": 0.60}
        ],
        international_ranking=85,
        
        # Infrastructure data (adequate)
        arena_capacity=5500,  # Avia Solutions Group Arena
        arena_modernity=0.75,
        training_facilities=0.70,
        auxiliary_platforms=0.65,
        airport_accessibility=0.80,  # Vilnius Airport
        railway_accessibility=0.75,
        other_transport=0.70,
        
        # Financial Stability data (moderate)
        budget=7500000,
        required_budget=9000000,  # Below requirement
        sponsorship_strength=0.70,
        media_partnership=0.65,
        financial_fair_play=[0.75, 0.70, 0.70, 0.65, 0.65],
        
        # Marketing Potential data (good in basketball-loving country)
        social_media_following=800000,
        average_attendance=4500,
        regional_market_size=0.60,  # Small market
        tv_broadcast_reach=0.60,
        digital_media_presence=0.65,
        tourism_attractiveness=0.75,  # Vilnius
        cultural_significance=0.80,  # Basketball in Lithuania
        international_accessibility=0.75,
        
        # Organizational Experience data (limited)
        international_events=[(0.6, 0.70), (0.5, 0.65), (0.5, 0.60)],
        management_qualification=0.70,
        communication_service=0.65,
        local_authority_partnership=0.70,
        sports_federation_partnership=0.65
    )
    teams.append(bc_wolves)
    
    # Karachi Royals (Pakistan) - Not Selected, Fictional
    karachi_royals = Team(
        id="KAR", 
        name="Karachi Royals", 
        continent="Asia", 
        region="South Asia",
        
        # Sporting Level data (Pakistani League)
        national_rankings=[1.0, 0.95, 1.0, 0.95, 0.90],  # Dominant domestically but weak league
        continental_participations=[
            {"South Asian Club Championship": 0.60}, {"South Asian Club Championship": 0.65}, 
            {"South Asian Club Championship": 0.60}, {"South Asian Club Championship": 0.55}, 
            {"South Asian Club Championship": 0.55}
        ],
        international_ranking=150,  # Low international ranking
        
        # Infrastructure data (inadequate)
        arena_capacity=5000,  # Minimum threshold
        arena_modernity=0.50,
        training_facilities=0.50,
        auxiliary_platforms=0.45,
        airport_accessibility=0.75,  # Karachi Airport
        railway_accessibility=0.65,
        other_transport=0.55,
        
        # Financial Stability data (uncertain)
        budget=6500000,
        required_budget=9000000,  # Well below requirement
        sponsorship_strength=0.60,
        media_partnership=0.55,
        financial_fair_play=[0.65, 0.60, 0.60, 0.55, 0.55],
        
        # Marketing Potential data (developing)
        social_media_following=1200000,
        average_attendance=3500,
        regional_market_size=0.70,  # Large population but low basketball interest
        tv_broadcast_reach=0.50,
        digital_media_presence=0.60,
        tourism_attractiveness=0.55,
        cultural_significance=0.50,  # Cricket-dominated culture
        international_accessibility=0.50,  # Travel concerns
        
        # Organizational Experience data (limited)
        international_events=[(0.5, 0.60), (0.4, 0.55), (0.4, 0.50)],
        management_qualification=0.60,
        communication_service=0.55,
        local_authority_partnership=0.65,
        sports_federation_partnership=0.60
    )
    teams.append(karachi_royals)
    
    # AS Sale (Morocco) - Not Selected
    as_sale = Team(
        id="ASS", 
        name="AS Sale", 
        continent="Africa", 
        region="North Africa",
        
        # Sporting Level data (Moroccan League, BAL)
        national_rankings=[1.0, 0.95, 1.0, 0.95, 0.90],  # Strong domestically
        continental_participations=[
            {"Basketball Africa League": 0.80}, {"Basketball Africa League": 0.75}, 
            {"Basketball Africa League": 0.70}, {"FIBA Africa Champions Cup": 0.75}, 
            {"FIBA Africa Champions Cup": 0.70}
        ],
        international_ranking=90,
        
        # Infrastructure data (adequate)
        arena_capacity=5000,  # Minimum threshold
        arena_modernity=0.60,
        training_facilities=0.60,
        auxiliary_platforms=0.55,
        airport_accessibility=0.75,  # Rabat-Salé Airport
        railway_accessibility=0.70,
        other_transport=0.65,
        
        # Financial Stability data (moderate)
        budget=7000000,
        required_budget=9000000,  # Below requirement
        sponsorship_strength=0.65,
        media_partnership=0.60,
        financial_fair_play=[0.70, 0.70, 0.65, 0.65, 0.60],
        
        # Marketing Potential data (regional)
        social_media_following=900000,
        average_attendance=4500,
        regional_market_size=0.65,
        tv_broadcast_reach=0.60,
        digital_media_presence=0.65,
        tourism_attractiveness=0.75,  # Near Rabat
        cultural_significance=0.70,
        international_accessibility=0.70,
        
        # Organizational Experience data (moderate)
        international_events=[(0.7, 0.65), (0.6, 0.65), (0.5, 0.60)],
        management_qualification=0.65,
        communication_service=0.60,
        local_authority_partnership=0.70,
        sports_federation_partnership=0.65
    )
    teams.append(as_sale)
    
    # Brisbane Bullets (Australia) - Not Selected
    brisbane_bullets = Team(
        id="BRB", 
        name="Brisbane Bullets", 
        continent="Oceania", 
        region="Australia",
        
        # Sporting Level data (NBL mid-tier)
        national_rankings=[0.70, 0.65, 0.75, 0.70, 0.80],  # Inconsistent in NBL
        continental_participations=[
            {"NBL": 0.70}, {"NBL": 0.65}, {"NBL": 0.75}, 
            {"NBL": 0.70}, {"NBL": 0.80}
        ],
        international_ranking=75,
        
        # Infrastructure data (decent)
        arena_capacity=5000,  # Nissan Arena
        arena_modernity=0.70,
        training_facilities=0.75,
        auxiliary_platforms=0.70,
        airport_accessibility=0.85,  # Brisbane Airport
        railway_accessibility=0.75,
        other_transport=0.75,
        
        # Financial Stability data (moderate)
        budget=8000000,
        required_budget=9000000,  # Below requirement
        sponsorship_strength=0.70,
        media_partnership=0.65,
        financial_fair_play=[0.75, 0.70, 0.70, 0.65, 0.65],
        
        # Marketing Potential data (regional)
        social_media_following=900000,
        average_attendance=5000,
        regional_market_size=0.70,  # Brisbane market
        tv_broadcast_reach=0.65,
        digital_media_presence=0.70,
        tourism_attractiveness=0.80,  # Brisbane
        cultural_significance=0.65,
        international_accessibility=0.75,
        
        # Organizational Experience data (moderate)
        international_events=[(0.6, 0.70), (0.5, 0.65), (0.5, 0.65)],
        management_qualification=0.70,
        communication_service=0.65,
        local_authority_partnership=0.70,
        sports_federation_partnership=0.65
    )
    teams.append(brisbane_bullets)
    
    # Nantes Basket (France) - Not Selected, Fictional
    nantes_basket = Team(
        id="NTB", 
        name="Nantes Basket", 
        continent="Europe", 
        region="Western Europe",
        
        # Sporting Level data (French LNB Pro A mid-tier)
        national_rankings=[0.75, 0.70, 0.65, 0.75, 0.70],  # Mid-table French league
        continental_participations=[
            {"FIBA Europe Cup": 0.65}, {"FIBA Europe Cup": 0.60}, 
            {"FIBA Europe Cup": 0.65}, {"FIBA Europe Cup": 0.60}, 
            {"FIBA Europe Cup": 0.55}
        ],
        international_ranking=95,
        
        # Infrastructure data (adequate)
        arena_capacity=5500,  # La Trocardière
        arena_modernity=0.70,
        training_facilities=0.70,
        auxiliary_platforms=0.65,
        airport_accessibility=0.80,  # Nantes Atlantique
        railway_accessibility=0.85,  # Strong French rail
        other_transport=0.75,
        
        # Financial Stability data (modest)
        budget=7500000,
        required_budget=9000000,  # Below requirement
        sponsorship_strength=0.65,
        media_partnership=0.60,
        financial_fair_play=[0.75, 0.70, 0.70, 0.65, 0.65],
        
        # Marketing Potential data (local focus)
        social_media_following=600000,
        average_attendance=4500,
        regional_market_size=0.60,
        tv_broadcast_reach=0.55,
        digital_media_presence=0.65,
        tourism_attractiveness=0.75,  # Nantes
        cultural_significance=0.60,
        international_accessibility=0.85,  # Good European connections
        
        # Organizational Experience data (limited)
        international_events=[(0.6, 0.65), (0.5, 0.65), (0.5, 0.60)],
        management_qualification=0.65,
        communication_service=0.60,
        local_authority_partnership=0.70,
        sports_federation_partnership=0.60
    )
    teams.append(nantes_basket)
    
    return teams


def run_team_selection():
    """Run the team selection process with all teams"""
    # Create all teams
    all_teams = create_all_teams()
    
    selector = GSLTeamSelector(all_teams)
    
    scores_df = selector.get_team_scores_df()
    print("Team Scores (Sorted by Overall Score):")
    print(scores_df.sort_values('overall_score', ascending=False))
    
    # Select 24 teams
    selected_teams = selector.select_teams(num_teams=24)
    
    print("\nSelected 24 Teams:")
    for i, team in enumerate(selected_teams, 1):
        print(f"{i}. {team.name} ({team.continent}) - Score: {selector.team_scores[team.id]:.4f}")
    
    # Print continent distribution
    print("\nContinent Distribution:")
    for continent, count in selector.continent_counts.items():
        print(f"{continent}: {count} teams")
    
    all_team_ids = {team.id for team in all_teams}
    selected_team_ids = {team.id for team in selected_teams}
    non_selected_ids = all_team_ids - selected_team_ids
    
    print("\nTeams Not Selected:")
    for team in all_teams:
        if team.id in non_selected_ids:
            print(f"{team.name} ({team.continent}) - Score: {selector.team_scores[team.id]:.4f}")


if __name__ == "__main__":
    run_team_selection()
