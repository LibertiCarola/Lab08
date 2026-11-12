from database.distributore_DAO import DistributoreDAO
from database.prezzo_DAO import PrezzoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._distributori = None               #
        self.load_distributori()                # lista di oggetti_distributori con id, nome, indirizzo

        self.__sequenza_ottima = []             #
        self.__costo_ottimo = -1                #

    def load_distributori(self):
        """ Carica tutti i distributori e li setta nella variabile self._distributori """
        self._distributori = DistributoreDAO.get_distributori()

    def get_prezzo_medio(self, mese:int):
        """
        Calcola, per ogni distributore, il prezzo medio al litro per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome del distributore, media), es. (Distributore A, 1.789)
        """
        lista_distributori_prezzo_medio = []
        for distributore in self._distributori:
            dati_prezzi = PrezzoDAO.get_prezzi(distributore.id)                                                         # importiamo tutti i dati del singolo distributore in una lista

            lista_prezzi_mese = []
            for campo in dati_prezzi:
                if campo.data.month == mese:
                    lista_prezzi_mese.append(campo.prezzo_litro)                                                        # otteniamo una lista con tutti i prezzi di un dato mese in uno specifico distributore
            PrezzoMedio= sum(lista_prezzi_mese) / len(lista_prezzi_mese)
            tupla_distributore = (distributore.nome, PrezzoMedio)
            lista_distributori_prezzo_medio.append(tupla_distributore)
        return lista_distributori_prezzo_medio


    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di rifornimenti nei primi 7 giorni
        :return: sequenza di nomi distributore ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        prezzi_settimana = self.__get_prezzi_prima_settimana_mese(mese)
                                                                                            # dict[id.distrib] = lisa prezzi settimana n
        self.__ricorsione([], 1, None, 0, prezzi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {distributore.id: distributore.nome for distributore in self._distributori}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, round(self.__costo_ottimo, 2)
                                                                                        # dizionario con chiave=id.distributore e [lista prezzi prima settimana ORDINATI 0-6]
    def __ricorsione(self, sequenza_parziale, giorno, ultimo_distributore, costo_corrente, prezzi_settimana):
        """ Implementa la ricorsione """
        if giorno > 7:                                                                              # finito il settimo giorno
            if self.__costo_ottimo < 0:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)    # in questo modo otteniamo una lista autonoma e non un riferimento a una esistente
            elif costo_corrente < self.__costo_ottimo:                                                # fai confronti e aggiorna i vari campi
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = list(sequenza_parziale)
        else:                                                                                       # giorno n della settimana
            for distributore in self._distributori:
                prezzo_giorno_litro = prezzi_settimana[distributore.id][giorno-1]                   #calcola prezzo a litro del giorno in distributore corrente
                costo_carburante = prezzo_giorno_litro * 100                                        #calcola quanto spendi per 100l di pieno
                costo_spostamento = 0
                if ultimo_distributore is not None and ultimo_distributore != distributore.id:      #se devi campiare distributore aggiungi 5 euro
                    costo_spostamento = 5.0
                nuovo_costo = costo_corrente + costo_carburante + costo_spostamento                 #calcola spesa totale della giornata e sommalo a quella settimanale

                '''if distributore.id == 1:
                    lettera = 'A'
                else:
                    lettera = 'B'''''

                self.__ricorsione(sequenza_parziale = sequenza_parziale + [distributore.id],                #richiama ricorsione con nuovi valori
                                  giorno = giorno+1,
                                  ultimo_distributore = distributore.id,
                                  costo_corrente = nuovo_costo,
                                  prezzi_settimana = prezzi_settimana)


    def __get_prezzi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i prezzi dei primi 7 giorni del mese selezionato per ciascun distributore.
        :return: un dizionario: {id_distributore: [prezzo_giorno1, ..., prezzo_giorno7]}
        """
        distributori_prezzo_settimanale = {}
        for distributore in self._distributori:
            info_prezzi = PrezzoDAO.get_prezzi(distributore.id)

            distrib_prezzo = []
            for elemento in info_prezzi:
                    if elemento.data.month == mese and elemento.data.day<=7:
                        distrib_prezzo.append(elemento.prezzo_litro)
            distributori_prezzo_settimanale[distributore.id] = distrib_prezzo

        return distributori_prezzo_settimanale                      # restituisce un dizionario con chiave=id.distributore e [lista prezzi prima settimana ORDINATI 0-6]

