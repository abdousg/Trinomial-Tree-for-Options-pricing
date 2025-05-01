import math
import datetime
import time
import xlwings as xw
import matplotlib.pyplot as plt
from scipy.stats import norm
import networkx as nx

debut = time.perf_counter()


# Bienvenue dans le projet de Rajaratnam Arthikan et Gaye Abdoulaye

# Celui-ci consiste en la mise en place d'un arbre trinomial pour faire un pricing d'options

# Nous allons commencer par mettre en place les classes nous permettant de réussir ce pricing :

# Nous commençons par la classe Market qui contient les paramètres du marché

class Market:
    def __init__(self, vol, rate, spot, div, div_ex_date):
        self.vol = vol
        self.rate = rate
        self.spot = spot
        self.div = div
        self.div_ex_date = div_ex_date
        # Nous commençons par nommer les attributs de cette classe


class Option:
    def __init__(self, strike, maturity, is_call, is_am, market):
        self.strike = strike
        self.maturity = maturity
        self.is_call = is_call
        self.is_am = is_am
        self.market = market

    # On va mettre en place une méthode qui va calculer le payoff de notre option :
    def payoff(self, value):
        if self.is_call:
            p_o = max(value - self.strike, 0)
        else:
            p_o = max(self.strike - value, 0)
        return p_o


class Tree:
    def __init__(self, root_node, nb_steps, pricing_date, option, market):
        self.root_node = root_node
        self.nb_steps = nb_steps
        self.pricing_date = pricing_date
        self.option = option
        self.market = market

        # L'objet possède d'autres attributs, mais que l'on va définir ci-après
        self.delta_t = self.calc_delta_t()
        self.alpha = self.calc_alpha()
        self.capi_f = self.capitalization_factor()
        self.discount_f = self.discount_factor()

    # Définissons après les méthodes ci-dessus :

    def calc_delta_t(self):

        diff = (self.option.maturity - self.pricing_date).days
        delta_t = diff / self.nb_steps / 365
        return delta_t

    def capitalization_factor(self):
        capi_f = math.exp(self.market.rate * self.delta_t)
        return capi_f

    def calc_alpha(self):
        alpha = math.exp(self.market.vol * math.sqrt(3 * self.delta_t))
        return alpha

    def discount_factor(self):
        discount_f = math.exp(-self.market.rate * self.delta_t)
        return discount_f

    def calc_div_date(self):
        div_date = (self.market.div_ex_date - self.pricing_date).days / 365
        return div_date

    def black_scholes(self):
        # Vérifie si l'option est de type américain
        if self.option.is_am:
            # Si c'est le cas, retourne un message indiquant que le calcul n'est pas possible
            return "Il n'est pas possible de calculer Black - Scholes avec une option américaine"
        else:
            # Obtient les paramètres nécessaires pour le calcul de Black-Scholes
            s_0 = self.market.spot  # Prix actuel du sous-jacent
            k = self.option.strike  # Prix d'exercice de l'option
            r = self.market.rate  # Taux d'intérêt sans risque
            t = (self.option.maturity - self.pricing_date).days / 365  # Temps jusqu'à l'échéance en années
            sigma = self.market.vol  # Volatilité du sous-jacent

            # Calcul des parties d1 et d2 de la formule de Black-Scholes
            d1 = (math.log(s_0 / k) + (r + 0.5 * sigma ** 2) * t) / (sigma * math.sqrt(t))
            d2 = d1 - sigma * math.sqrt(t)

            # Calcul du prix de l'option en fonction de sa nature (call ou put)
            if self.option.is_call:
                price = s_0 * norm.cdf(d1) - k * math.exp(-r * t) * norm.cdf(d2)
            else:
                price = k * math.exp(-r * t) * norm.cdf(-d2) - s_0 * norm.cdf(-d1)

        # Retourne le prix calculé de l'option
        return price

    def calc_delta(self):
        # Le delta d'une option représente la variation du prix de l'option par rapport à la variation du prix spot

        # On appelle la création de l'arbre
        root_node_1 = Node(self.market.spot, 0, self.option, self.market)
        root_node_2 = Node(self.market.spot + 0.01, 0, self.option, self.market)

        # Construction de nos 2 arbres
        root_node_1.build_columns_of_nodes(self, self.option, self.market)
        root_node_2.build_columns_of_nodes(self, self.option, self.market)

        # Pricing de nos 2 arbres et calcul du delta :
        delta = (root_node_2.pricing(self) - root_node_1.pricing(
            self)) / 0.01  # On divise par le pas que l'on a choisi de prendre

        return delta

    def calc_gamma(self):  # Le gamma représente la dérivée seconde du prix par rapport au spot

        # On instancie les noeuds racines de nos 3 arbres:

        root_node_1 = Node(self.market.spot, 0, self.option, self.market)
        root_node_2 = Node(self.market.spot + 3.5, 0, self.option, self.market)
        root_node_3 = Node(self.market.spot - 3.5, 0, self.option, self.market)

        # Construction de nos 3 arbres
        root_node_1.build_columns_of_nodes(self, self.option, self.market)
        root_node_2.build_columns_of_nodes(self, self.option, self.market)
        root_node_3.build_columns_of_nodes(self, self.option, self.market)


        # Pricing de nos 3 arbres et calcul de nos 2 deltas :
        delta_1 = (root_node_1.pricing(self) - root_node_3.pricing(self)) / 3.5
        delta_2 = (root_node_2.pricing(self) - root_node_1.pricing(self)) / 3.5

        # Calcul du gamma :

        gamma = (delta_2 - delta_1)/3.5

        return gamma

    def vega_calculus(
            self):  # Le vega correspond à la variation du prix de l'option avec une augmentation de 1% de la volatilité du marché

        root_node_1 = Node(market.spot, 0, self.option, self.market)
        root_node_1.build_columns_of_nodes(self, self.option, self.market)
        res_1 = root_node_1.pricing(self)

        # On va changer la vol de la classe market
        self.market.vol = self.market.vol + 0.01  # On augmente la vol de 1% (par définition du vega)

        self.alpha = math.exp(self.market.vol * math.sqrt(3 * self.delta_t))

        root_node_1 = Node(market.spot, 0, self.option, self.market)
        root_node_1.build_columns_of_nodes(self, self.option, self.market)
        res_2 = root_node_1.pricing(self)

        vega = (res_2 - res_1)/0.01  # Agrégation du résultat

        return vega

    def tree_bs_conv(self):

        l_1 = []
        l_2 = []
        list_b_s_price = []
        list_tree_price = []

        for compt in range(100):  # 50 représente le nombre d'incréments de prix (donc le nombre d'itérations)
            self.option.strike += 1  # Pour incrémenter sur le prix de base
            root_node = Node(self.market.spot, 0, self.option, self.market)

            # Construction de l'arbre :
            root_node.build_columns_of_nodes(self, self.option, self.market)

            # Pricing:
            tree_price = root_node.pricing(self)
            b_s_price = self.black_scholes()
            gap = tree_price - b_s_price

            l_1.append(gap)
            l_2.append(self.option.strike)
            list_b_s_price.append(b_s_price)
            list_tree_price.append(tree_price)

        fig, ax1 = plt.subplots()

        ax1.set_xlabel('Spot Price')
        ax1.set_ylabel('Gap (Tree - Black-Scholes)',
                       color='tab:blue')  # On crée un nouvel axe pour faciliter la lecture du graphique
        ax1.plot(l_2, l_1, label='Gap (Tree - Black-Scholes)', color='tab:red')
        ax1.tick_params(axis='y', labelcolor='tab:blue')

        ax2 = ax1.twinx()
        ax2.set_ylabel('Price', color='red')
        ax2.plot(l_2, list_b_s_price, label='Black-Scholes Price', color='tab:green')
        ax2.plot(l_2, list_tree_price, label='Tree Price', color='tab:blue')
        ax2.tick_params(axis='y', labelcolor='tab:red')

        fig.tight_layout()

        # Ajouter une légende
        fig.legend(loc='upper right')

        # Afficher le graphique
        plt.show()

    def tree_bs_tunnel(self):
        l_1 = []
        l_2 = []
        root_node = Node(self.market.spot, 0, self.option, self.market)

        self = class_tree_initialize(root_node)  # On instancie la classe arbre

        self.nb_steps = 1

        for compt in range(300):  # 100 représente le nombre d'incréments de pas de l'arbre

            # On recalcule les attributs de notre arbre :

            self.delta_t = self.calc_delta_t()
            self.alpha = self.calc_alpha()
            self.capi_f = self.capitalization_factor()
            self.discount_f = self.discount_factor()

            # Construction de l'arbre :
            root_node.build_columns_of_nodes(self, self.option, self.market)
            # Pricing:
            tree_price = root_node.pricing(self)
            b_s_price = self.black_scholes()
            gap = (tree_price - b_s_price)

            # Création des deux listes pour construire notre graphique
            l_1.append(gap*self.nb_steps)
            l_2.append(self.nb_steps)

            root_node = Node(self.market.spot, 0, self.option, self.market)

            self = class_tree_initialize(root_node)  # On instancie la classe arbre

            self.nb_steps += compt +1 # On incrémente le nombre de pas de notre arbre

        plt.plot(l_2, l_1)
        plt.show()



# Enfin la classe Node qui va venir compléter le modèle

class Node:
    def __init__(self, value, time_st, option, market):
        # Les attributs que l'on connaît d'avance
        self.value = value
        self.time_st = time_st
        self.option = option
        self.market = market

        # L'objet possède d'autres attributs, mais que l'on va définir ci-après
        self.neighbour_up = None
        self.neighbour_down = None
        self.next_mid = None
        self.next_up = None
        self.next_down = None
        self.option_value = None  # Retourne le prix de l'option à ce noeud

    # Cette structure est très importante pour imbriquer les nœuds entre eux

    # Mise en place d'une méthode qui permet de calculer le noeud forward
    def forward(self, tree):
        if self.time_st < tree.calc_div_date() <= self.time_st + tree.delta_t:
            next_fwd = self.value * tree.capi_f - self.market.div
        else:
            next_fwd = self.value * tree.capi_f
        return next_fwd

    def move_up(self, tree):
        if self.neighbour_up is None:
            n_up = Node(self.value * tree.alpha, self.time_st, option, market)
        return n_up

    def move_down(self, tree):
        if self.neighbour_down is None:
            n_down = Node(self.value / tree.alpha, self.time_st, option, market)
        return n_down

    def build_columns_of_nodes(self, tree, option, market):
        # Nous arrivons à un moment où l'arbre est construit jusqu'à une date t
        # Ici, nous partons du noeud du milieu de la date t pour construire la colonne de nœuds

        #tracker = self
        # Cette variable va nous permettre de vérifier que notre arbre est bien construit
        # A la date t+1 :
        for step in range(tree.nb_steps):  # Pour parcourir toutes les étapes de l'arbre
            compt = 0  # On met en place un compteur pour compter le nombre de noeud au-dessus du noeud médian
            Node_mid_spot = self.forward(tree)
            Node_mid = Node(Node_mid_spot, self.time_st + tree.delta_t, option, market)

            self.next_mid = Node_mid  # On se place sur le nœud médian
            node_to_connect_init = self  # On garde le nœud du début en mémoire
            node_to_connect = self
            # Ce nœud se place en t-1 il est important pour connecter les nœuds en t-1 à ceux en t
            node_to_conserve = Node_mid  # Ce noeud permettra la construction des nœuds haut et bas du mid de chaque étape

            self = Node_mid
            while compt <= step:
                Node_up = self.move_up(tree)  # On construit le noeud du haut du noeud actuel
                self.neighbour_up = Node_up  # Au noeud actuel, on lui attribue un voisin haut
                Node_up.neighbour_down = self  # Au voisin du haut, on lui attribue un voisin du bas
                node_to_connect.next_up = Node_up  # Au noeud en t-1, on lui attribue un next up
                node_to_connect.next_mid = self  # Au noeud en t-1 on lui attribue en next mid
                node_to_connect.next_down = self.neighbour_down  # Au noeud en t-1 on lui attribue en next down
                self = Node_up  # On se place sur le noeud voisin haut (en t)
                if node_to_connect.neighbour_up is None:  # Si le noeud en t-1 ne possède pas de voisin du haut
                    node_to_connect = node_to_connect  # On reste sur celui-ci
                else:
                    node_to_connect = node_to_connect.neighbour_up  # Sinon, le noeud en t-1 passe sur son voisin du haut
                compt += 1  # On recommence la construction jusqu'à ce qu'on ait atteint le nombre de nœuds
                # à construire au-dessus du noeud médian

            compt = 0  # compt reprend sa valeur initiale

            self = node_to_conserve  # On revient au noeud du milieu initial
            node_to_connect = node_to_connect_init  # On se replace au noeud gardé en mémoire plus haut

            while compt <= step:  # On va suivre le même processus pour construire les nœuds en dessous du noeud médian
                Node_down = self.move_down(tree)
                self.neighbour_down = Node_down
                Node_down.neighbour_up = self
                node_to_connect.next_down = Node_down
                node_to_connect.next_mid = self
                node_to_connect.next_up = self.neighbour_up
                self = Node_down
                node_to_connect = node_to_connect.neighbour_down
                compt += 1

            self = node_to_conserve

    # Une fois que les nœuds sont bien imbriqués entre eux, nous passons au calcul des probabilités :

    def variance(self, tree):
        exp_1 = self.value ** 2
        exp_2 = math.exp(2 * self.market.rate * tree.delta_t)
        exp_3 = math.exp(tree.market.vol ** (2) * tree.delta_t) - 1
        var = exp_1 * exp_2 * exp_3
        return var

    def p_down(self, tree):
        exp_1 = self.next_mid.value ** (-2) * (self.variance(tree) + self.forward(tree) ** (2)) - 1
        exp_2 = (self.next_mid.value ** (-1) * self.forward(tree) - 1) * (tree.alpha + 1)
        num = exp_1 - exp_2
        denom = (1 - tree.alpha) * (tree.alpha ** (-2) - 1)
        prob_down = num / denom
        return prob_down

    def p_up(self, tree):
        exp_1 = self.next_mid.value ** (-1) * self.forward(tree) - 1
        exp_2 = self.p_down(tree) * (tree.alpha ** (-1) - 1)
        denom = tree.alpha - 1
        prob_up = (exp_1 - exp_2) / denom
        return prob_up

    def p_mid(self, tree):
        prob_mid = 1 - (self.p_down(tree) + self.p_up(tree))
        return prob_mid

    # Nous allons passer au pricing

    def pricing(self, tree):
        if self.option_value is None:
            if self.next_mid is None:  # C'est notre condition d'arrêt !
                self.option_value = tree.option.payoff(self.value)  # On récupère le payoff
            else:

                if self.option_value is None:  # Cela nous évite de calculer cela plusieurs fois pour un même noeud
                    self.option_value = (
                            tree.discount_f * (
                            self.p_up(tree) * self.next_up.pricing(tree) +
                            self.p_mid(tree) * self.next_mid.pricing(tree) +
                            self.p_down(tree) * self.next_down.pricing(tree)
                    )
                    )

                if self.option.is_am:
                    self.option_value = max(self.option_value, self.option.payoff(self.value))

        return self.option_value


# Nous allons maintenant nous occuper du pruning:


################################### TEST ##################################
################################### TEST ##################################
################################### TEST ##################################
################################### TEST ##################################
################################### TEST ##################################


# On initialise la classe Market grâce à xlwings

def class_market_initialize():
    wb = xw.Book("projet_abdou_arthi.xlsm")
    sheet_main = wb.sheets["Pricing"]

    # On initialise la classe Market

    vol = sheet_main["rg_vol"].value
    spot = sheet_main["rg_spot"].value
    rate = sheet_main["rg_rate"].value
    div = sheet_main["rg_div"].value
    div_date = sheet_main["div_date"].value

    market_instance = Market(vol, rate, spot, div, div_date)

    return market_instance


# On initialise la classe Option grâce à xlwings

def class_option_initialize():
    wb = xw.Book("projet_abdou_arthi.xlsm")
    sheet_main = wb.sheets["Pricing"]

    strike = sheet_main["rg_strike"].value
    maturity = sheet_main["rg_mat"].value

    is_call = sheet_main["range_call"].value
    is_call = eval(is_call)  # Pour transformer notre expression en booléen

    is_am = sheet_main["range_am"].value
    is_am = eval(is_am)

    market = class_market_initialize()

    option_instance = Option(strike, maturity, is_call, is_am, market)

    return option_instance

    # On initialise notre arbre :


def class_tree_initialize(root_node):
    wb = xw.Book("projet_abdou_arthi.xlsm")
    sheet_main = wb.sheets["Pricing"]

    nb_steps = sheet_main["n_steps"].value
    nb_steps = int(nb_steps)  # On convertit le nombre de steps en integer
    pricing_date = sheet_main["prc_date"].value

    option = class_option_initialize()

    market = class_market_initialize()

    tree_instance = Tree(root_node, nb_steps, pricing_date, option, market)

    return tree_instance


market = class_market_initialize() # Instance de notre classe market
option = class_option_initialize() # Instance de notre classe option
root_node = Node(market.spot, 0, option, market) # Instance de notre noeud racine
tree = class_tree_initialize(root_node) # Instance de notre classe tree

root_node.build_columns_of_nodes(tree, option, market)  # Pour la construction de notre arbre avant de faire le pricing

prix = root_node.pricing(tree)

print("option price is : " + str(prix)) # Pour le pricing de notre option

print("price with Black-Scholes is : " + str(tree.black_scholes())) # Pour calculer le prix via Black - Scholes

#tree.tree_bs_conv()
#tree.tree_bs_tunnel()

print("delta is : " + str(tree.calc_delta())) # Pour calculer le delta
print("gamma is : " + str(tree.calc_gamma())) # Pour calculer le gamma
print("vega is : " + str(tree.vega_calculus())) # Pour calculer le vega

fin = time.perf_counter()
duree = fin - debut
print("\n""time to execute the code is :  " + str(duree) + " seconds") # Pour calculer la durée d'exécution du code

# On va rajouter le prix sur xlwings :

wb = xw.Book("projet_abdou_arthi.xlsm")
sheet_main = wb.sheets["Pricing"]

sheet_main['rg_prix_pyt'].value = prix