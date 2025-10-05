# /fiscweb/models.py
# Rev 0
import os
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import datetime, timedelta

#====================================================FUNÇÃO DE TRATAMENTO DOS ARQUIVOS ANEXOS================================================
def caminho_PS(instance, filename):
        """Função genérica que encontra PassServ automaticamente"""
        
        # Buscar campo ForeignKey para PassServ
        pass_serv = None
        for field in instance._meta.get_fields():
            if hasattr(field, 'related_model') and field.related_model == PassServ:
                pass_serv = getattr(instance, field.name)
                break
        
        if not pass_serv:
            raise ValueError("Modelo não tem relacionamento com PassServ")
        
        folder = instance.PASTA_UPLOAD
        # Resto igual
        barco = pass_serv.BarcoPS
        num_ps = pass_serv.numPS
        data_emissao = pass_serv.dataEmissaoPS
        ano = data_emissao.year
        
        nome_original, extensao = os.path.splitext(filename)
        data_formatada = data_emissao.strftime('%d-%m-%Y')
        nome_arquivo = f"{num_ps} - {data_formatada} - {nome_original}{extensao}"
        
        return f"storage/PS/{barco}/{ano}/{folder}/{nome_arquivo}"


#================================================TABELAS DE APOIO - MODELO MODAL BARCO==============================================#
class ModalBarco(models.Model):
    """Modelo para cadastro de Modais de barcos """
       
    # Campos
    modal = models.CharField(max_length=20,verbose_name='Modal')
    def __str__(self):
        return self.modal
    
    class Meta:
        verbose_name = 'Modal'
        verbose_name_plural = "Modais"


#================================================MODELO FISCAIS CADASTRO================================================#
class FiscaisCad(models.Model):
    """Modelo para cadastro de fiscaiss"""
      
    celular_validator = RegexValidator(
        regex=r'^\(\d{2}\)\d{4,5}-\d{4}$',
        message='Celular deve estar no formato: (99)99999-9999'
    )
    
    # Campos
    chave = models.CharField(max_length=4,verbose_name='Chave', unique=True)
    nome = models.CharField(max_length=80, verbose_name='Nome')
    email = models.EmailField(max_length=40, verbose_name='E-mail')
    celular = models.CharField(max_length=15,validators=[celular_validator],blank=True,verbose_name='Celular' )
    # Campos automáticos
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Fiscal'
        verbose_name_plural = 'Fiscais'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    

#================================================MODELO BARCOS CADASTRO================================================#
class BarcosCad(models.Model):
    """Modelo para cadastro de embarcações"""
    
    barcoTipoChoice =   [
                        ('rsv'   , 'RSV'),
                        ('sdsv'  , 'SDSV'),
                        ('dsv'   , 'DSV'),
                        ('tup'   , 'TUP'),
                                          ]
           
    tipoBarco = models.CharField(max_length=6,choices=barcoTipoChoice, verbose_name='Tipo')
    nomeBarco = models.CharField(max_length=50, verbose_name='Nome',unique=True)
    modalSelec = models.ForeignKey(ModalBarco,on_delete=models.SET_NULL,null=True, blank=True,verbose_name='Seleciona Modal')    
    modalBarco=models.CharField(max_length=20,verbose_name='Modal')
    emailPetr = models.EmailField(max_length=40, verbose_name='E-mail Petrobras',unique=True)
    dataPrimPorto = models.DateField(verbose_name='Data Primeiro Porto')
    emprNav = models.CharField(max_length=80,verbose_name='Empresa Navegação')
    icjEmprNav = models.CharField(max_length=20,verbose_name='ICJ Empresa Navegação', unique=True)
    emprServ = models.CharField(max_length=80,verbose_name='Empresa Serviço')
    icjEmprServ = models.CharField(max_length=20,verbose_name='ICJ Empresa Serviço', unique=True)

     
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Barco'
        verbose_name_plural = 'Barcos'
        ordering = ['nomeBarco']
    
    def __str__(self):
        return f"{self.tipoBarco} - {self.nomeBarco}"
    
    def save(self, *args, **kwargs):
        # COPIA o nome da categoria selecionada
        if self.modalSelec:
            self.modalBarco = self.modalSelec.modal

        super().save(*args, **kwargs)
    


#================================================ 1 MODELO PASSAGENS DE SERVIÇO================================================#
class PassServ(models.Model):
    """Modelo para cadastro de Passagem de Serviço"""

     
    numPS = models.IntegerField(verbose_name='Numero da PS')
    anoPS=models.CharField(max_length=5,verbose_name='Ano da PS')
    dataInicio = models.DateField(verbose_name='Inicio da Quinzena')
    dataFim = models.DateField(verbose_name='Fim da Quinzena')
    dataEmissaoPS = models.DateField(verbose_name='Data de Emissao',default='2025-01-01')
    TipoBarco = models.CharField(max_length=6,verbose_name='Barco')
    BarcoPS = models.CharField(max_length=30,verbose_name='Barco')
    statusPS = models.CharField(max_length=12,verbose_name='Status da PS')
    fiscalEmb = models.CharField(max_length=30,verbose_name='Fiscal Embarcando')
    fiscalDes = models.CharField(max_length=30,verbose_name='Fiscal Desembarcando')
    
     
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Passagem de Serviço'
        verbose_name_plural = 'Passagens de serviço'
        ordering = ['BarcoPS','-numPS']
    
    def __str__(self):
        return f"{self.numPS} - {self.BarcoPS} - {self.dataEmissaoPS}"
        

#===========================================================1.1 =MODELO PORTO TROCA DE TURMA===============================================
class PortoTrocaTurma(models.Model):
    """Modelo para cadastro de Passagem de Serviço - Porto"""

    idxPortoTT = models.ForeignKey(PassServ,on_delete=models.CASCADE)

    Porto = models.CharField(max_length=40,verbose_name='Porto')
    Terminal = models.CharField(max_length=40,verbose_name='Terminal')
    OrdSerPorto = models.CharField(max_length=12,verbose_name='Ordem de Serviço')
    AtracPorto = models.DateField(verbose_name='Horario da Atracação')
    DuracPorto = models.CharField(max_length=6,verbose_name='Duração da estadia(h)')
    ObservPorto = models.TextField(max_length=500,verbose_name='Observações', blank=True)
    class Meta:
        verbose_name = 'Troca de Turma - Porto'
        verbose_name_plural = 'Trocas de Turma - Portos'
        ordering = ['idxPortoTT__BarcoPS','-idxPortoTT__numPS']
    
    def __str__(self):
        return f"{self.idxPortoTT} - {self.Porto}"
    


#==========================================================1.2 MODELO PORTO MANUTENÇÃO PREVENTIVA===============================================
class PortoManutPrev(models.Model):
    """Modelo para cadastro de Passagem de Serviço - Manutenção Preventiva - porto"""

    PASTA_UPLOAD = 'Rade'

    idxPortoMP = models.ForeignKey(PassServ, on_delete=models.CASCADE)

    prevManPrev = models.BooleanField(default=False, verbose_name='Manutenção preventiva prevista?')

    Franquia = models.IntegerField(verbose_name='Franquia solicitada')
    SaldoFranquia = models.IntegerField(verbose_name='Saldo de Franquia')
    OrdSerManutPrev = models.CharField(max_length=12, verbose_name='Ordem de Serviço')
    Rade = models.FileField(upload_to=caminho_PS,verbose_name='Anexo Rade')
    ObservManPrev = models.TextField(max_length=500, verbose_name='Observações', blank=True)
    
    class Meta:
        verbose_name = 'Manutenção Preventiva - Porto'
        verbose_name_plural = 'Manutenções Preventivas - Portos'
        ordering = ['idxPortoMP__BarcoPS','-idxPortoMP__numPS']  
        
    def __str__(self):
        return f"{self.idxPortoMP} - {self.OrdSerManutPrev}"
    

#==========================================================1.3 MODELO PORTO ABASTECIMENTO===============================================
class PortoAbast(models.Model):
    """Modelo para cadastro de Passagem de Serviço - Abastecimento - porto"""

    PASTA_UPLOAD = 'Abast'

    idxPortoAB = models.ForeignKey(PassServ, on_delete=models.CASCADE)

    prevAbast = models.BooleanField(default=False, verbose_name='Abastecimento previsto?')

    OrdSerAbast = models.CharField(max_length=12, verbose_name='Ordem de Serviço')
    DataHoraPrevAbast = models.DateTimeField(verbose_name='Data e Hora Prevista')
    QuantAbast = models.IntegerField(verbose_name='Quantidade (m³)')
    DuracPrev = models.IntegerField(verbose_name='Duração Prevista(h)')
    UltAbast = models.DateField(verbose_name='Último Abastecimento')
    Anexos = models.FileField(upload_to=caminho_PS,verbose_name='Anexos')
    ObservManPrev = models.TextField(max_length=500, verbose_name='Observações', blank=True)
    
    class Meta:
        verbose_name = 'Abastecimento - Porto'
        verbose_name_plural = 'Abastecimentos - Portos'
        ordering = ['idxPortoAB__BarcoPS','-idxPortoAB__numPS']  

    def __str__(self):
        return f"{self.idxPortoAB} - {self.OrdSerAbast}"
    

#==========================================================1.4 MODELO INSPEÇÕES NORMATIVAS===============================================
class PortoInspNorm(models.Model):
    """Modelo para cadastro de Passagem de Serviço - Inspeções Normativas - porto"""

    inspNormDescChoices = [
                            ('anvisa' , 'ANVISA'),
                            ('classe' , 'CLASSE'),
                            ('marinha','MARINHA'),
                            ('outros' , 'OUTROS'),
                                                  ]

    idxPortoIN = models.ForeignKey(PassServ, on_delete=models.CASCADE)

    prevInsNorm = models.BooleanField(default=False, verbose_name='Inspeção Normativa?')

    DescInspNorm = models.CharField(max_length=9,choices=inspNormDescChoices,verbose_name='Inspeções Normativas')
    OrdSerInspNorm = models.CharField(max_length=12, verbose_name='Ordem de Serviço')
    ObservInspNorm = models.TextField(max_length=500, verbose_name='Observações', blank=True)
    
    class Meta:
        verbose_name = 'Inspeção Normativa - Porto'
        verbose_name_plural = 'Inspeções Normativas - Portos'
        ordering = ['idxPortoIN__BarcoPS','-idxPortoIN__numPS']  

    def __str__(self):
        return f"{self.idxPortoIN} - {self.DescInspNorm}"
    
#==========================================================1.5 MODELO INSPEÇÕES PETROBRAS===============================================
class PortoInspPetr(models.Model):
    """Modelo para cadastro de Passagem de Serviço - Inspeções Petrobras - porto"""

    inspPetrDescChoices = [
                            ('gsopsms'  ,'GSOP/SMS'),
                            ('gercontr' ,'GERENCIA CONTRATO'),
                            ('geroper'  ,'GERENTE OPERACIONAL'),
                            ('sto'      ,'STO'),
                            ('outros'   ,'OUTROS'),
                          ]

    idxPortoIP = models.ForeignKey(PassServ, on_delete=models.CASCADE)

    prevInspPetr = models.BooleanField(default=False, verbose_name='Inspeção Petrobras?')

    DescInspPetr = models.CharField(max_length=9,choices=inspPetrDescChoices,verbose_name='Inspeções Petrobras')
    auditorPetr = models.CharField(max_length=30, verbose_name='Auditor/Visitante')
    gerAuditorPetr = models.CharField(max_length=30, verbose_name='Gerencia')
    ObservInspPetr = models.TextField(max_length=500, verbose_name='Observações', blank=True)
    
    class Meta:
        verbose_name = 'Inspeção Petrobras - Porto'
        verbose_name_plural = 'Inspeções Petrobras - Portos'
        ordering = ['idxPortoIP__BarcoPS','-idxPortoIP__numPS']  

    def __str__(self):
        return f"{self.idxPortoIP} - {self.DescInspPetr}"
    

#==========================================================1.6 MODELO EMBARQUE EQUIPES===============================================
class PortoEmbEquip(models.Model):
    """Modelo para cadastro de Passagem de Serviço - Embarque Equipes - porto"""

    EmbEquipDescChoices = [
                            ('crd'     ,'CRD'),
                            ('stc'     ,'STC'),
                            ('eqse'    ,'EQSE'),
                            ('sto'     ,'STO'),
                            ('cenpes'  ,'CENPES'),
                            ('ambient' ,'AMBIENTAÇÃO'),
                            ('outros'   ,'OUTROS'),
                          ]

    idxPortoEE = models.ForeignKey(PassServ, on_delete=models.CASCADE)

    prevEmbEquip = models.BooleanField(default=False, verbose_name='Embarque de Equipe?')

    DescEmbEquip = models.CharField(max_length=9,choices=EmbEquipDescChoices,verbose_name='Descrição')
    equipNome = models.CharField(max_length=30, verbose_name='Nome')
    equipEmpre = models.CharField(max_length=30, verbose_name='Empresa')
    ObservEmbEquip = models.TextField(max_length=200, verbose_name='Observações', blank=True)
    
    class Meta:
        verbose_name = 'Embarque Equipe - Porto'
        verbose_name_plural = 'Embarque Equipes - Portos'
        ordering = ['idxPortoEE__BarcoPS','-idxPortoEE__numPS']  

    def __str__(self):
        return f"{self.idxPortoEE} - {self.DescEmbEquip}"
    

#==========================================================1.7 MODELO EMBARQUE MATERIAIS===============================================
class PortoEmbMat(models.Model):
    """Modelo para cadastro de Passagem de Serviço - Embarque de Materiais - porto"""

    PASTA_UPLOAD = 'EmbMaterial'

    idxPortoEM = models.ForeignKey(PassServ, on_delete=models.CASCADE)

    prevEmbMat = models.BooleanField(default=False, verbose_name='Embarque de Materiais?')

    OsEmbMat = models.CharField(max_length=12,verbose_name='OS de Destino')
    RtEmbMat = models.CharField(max_length=12, verbose_name='Num RT')
    ObservEmbMat = models.TextField(max_length=200, verbose_name='Observações', blank=True)
    Anexos = models.FileField(upload_to=caminho_PS,verbose_name='Anexo')

    class Meta:
        verbose_name = 'Embarque Material - Porto'
        verbose_name_plural = 'Embarque Materiais - Portos'
        ordering = ['idxPortoEM__BarcoPS','-idxPortoEM__numPS']  

    def __str__(self):
        return f"{self.idxPortoEM} - {self.RtEmbMat}"
    

#==========================================================1.8 MODELO DESEMBARQUE MATERIAIS===============================================
class PortoDesMat(models.Model):
    """Modelo para cadastro de Passagem de Serviço - Desembarque de Materiais - porto"""

    PASTA_UPLOAD = 'DesembMaterial'

    idxPortoDM = models.ForeignKey(PassServ, on_delete=models.CASCADE)

    prevDesMat = models.BooleanField(default=False, verbose_name='Desembarque de Materiais?')

    OsDesMat = models.CharField(max_length=12,verbose_name='OS de Origem')
    RtDesMat = models.CharField(max_length=12, verbose_name='Num RT')
    ObservDesMat = models.TextField(max_length=500, verbose_name='Observações', blank=True)
    Anexos = models.FileField(upload_to=caminho_PS,verbose_name='Anexo')

    class Meta:
        verbose_name = 'Desembarque Material - Porto'
        verbose_name_plural = 'Desembarque Materiais - Portos'
        ordering = ['idxPortoDM__BarcoPS','-idxPortoDM__numPS']  

    def __str__(self):
        return f"{self.idxPortoDM} - {self.RtDesMat}"
    

#==========================================================1.9 MODELO MOBILIZAÇÃO DESMOBILIZAÇÃO===============================================
class PortoMobD(models.Model):
    """Modelo para cadastro de Passagem de Serviço - Operações de Mobilização e desmobilização - Porto"""

    idxPortoMobD = models.ForeignKey(PassServ, on_delete=models.CASCADE)

    prevMobD = models.BooleanField(default=False, verbose_name='Mobilização ou Desmobilização?')

    OsMobD = models.CharField(max_length=12,verbose_name='OS de Origem')
    ObservMobD = models.TextField(max_length=500, verbose_name='Observações', blank=True)
    
    class Meta:
        verbose_name = 'MObilização e Desmobilização - Porto'
        verbose_name_plural = 'Mobilizações Desmobilizações - Portos'
        ordering = ['idxPortoMobD__BarcoPS','-idxPortoMobD__numPS']  

    def __str__(self):
        return f"{self.idxPortoMobD} - {self.OsMobD}"
    


#===========================================================2.0 MODELO ANOMALIAS E CORRENCIAS DE SMS===========================================
class anocSMS(models.Model):
    """Modelo para cadastro de Passagem de Serviço - Anomalias e Ocorrencias de SMS"""

    classanocSMSChoices=[   
                            ('critica','CRÍTICA'),
                            ('nao_critica','NÃO CRITICA'),
                            ]
    
    informContrChoices=[
                            ('sim','SIM'),
                            ('nao','NÃO'),
                            ]

    idxanocSMS = models.ForeignKey(PassServ, on_delete=models.CASCADE)

    prevanocSMS = models.BooleanField(default=False, verbose_name='Anomalias?')

    DataanocSMS = models.DateField(verbose_name='Data da Anomalia')
    classnocSMS = models.CharField(max_length=12,choices=classanocSMSChoices, verbose_name='Classificação da Anomalia')
    DescanocSMS = models.TextField(max_length=500, verbose_name='Descrição da Anomalia', blank=True)
    informContr = models.CharField(max_length=4, choices=informContrChoices, verbose_name='Houve Informe ao Controle?')
    
    class Meta:
        verbose_name = 'Anomalia e Ocorrência de SMS'
        verbose_name_plural = 'Anomalias e Ocorrêcias de SMS'
        ordering = ['idxanocSMS__BarcoPS','-idxanocSMS__numPS']  

    def __str__(self):
        return f"{self.idxanocSMS} - {self.classnocSMS}" 
    

#===========================================================3 MODELO INOPERANCIAS PENDENCIAS E ASSUNTOS CONTRATUAIS===========================================
class inoPendContr(models.Model):
    """Modelo para cadastro de Passagem de Serviço - Inoperâncias Pendências e assuntos Contratuais"""

    
    inoPendContrConfChoices=[
                            ('sim' ,'SIM'),
                            ('nao' ,'NÃO'),
                            ('n_ap','N/A'),
                            ]

    idxinoPendContr = models.ForeignKey(PassServ, on_delete=models.CASCADE)

    previnoPendContr = models.BooleanField(default=False, verbose_name='Anomalias?')

    DatainoPendContr = models.DateField(verbose_name='Data da Anomalia')
    DescinoPendContr = models.TextField(max_length=500, verbose_name='Descrição', blank=True)
    BroainoPendContr = models.CharField(max_length=4, choices=inoPendContrConfChoices, verbose_name='Abertura de BROA?')
    NumBroainoPendContr = models.CharField(max_length=12, verbose_name='Num BROA', blank=True)
    infGerContinoPendContr = models.CharField(max_length=4, choices=inoPendContrConfChoices, verbose_name='Houve Informe a Gerência de Contrato?')
    class Meta:
        verbose_name = 'Inoperância,Pendencia e Assunto Contratual'
        verbose_name_plural = 'Inoperâncias,Pendencias e Assuntos Contratuais'
        ordering = ['idxinoPendContr__BarcoPS','-idxinoPendContr__numPS']  

    def __str__(self):
        return f"{self.idxinoPendContr}" 
    

 #===========================================================4 MODELO ROTINAS===========================================

 #-==========================================================4.1 IAPO===================================================
class iapo(models.Model):
    """Modelo para cadastro de Passagem de Serviço - IAPO - Rotinas"""

    iapoConfChoices=[
                        ('sim' ,'SIM'),
                        ('nao' ,'NÃO'),
                        ('n_ap','N/A'),
                        ]

    idxIapo = models.ForeignKey(PassServ, on_delete=models.CASCADE)

    priDomIapo = models.DateField(verbose_name='IAPO Primeira Semana')
    priDomIapoOs = models.CharField(max_length=4, choices=iapoConfChoices, verbose_name='OSs para IAPO?')
    segDomIapo = models.DateField(verbose_name='IAPO Segunda Semana')
    segDomIapoOs = models.CharField(max_length=4, choices=iapoConfChoices, verbose_name='OSs para IAPO?')
    terDomIapo = models.DateField(verbose_name='IAPO Terceira Semana')  # Corrigido
    terDomIapoOsConc = models.CharField(max_length=4, choices=iapoConfChoices, verbose_name='OSs concluidas para esse envio?')
    ObservIapo = models.TextField(max_length=500, verbose_name='Observações', blank=True)

    class Meta:
        verbose_name = 'IAPO'
        ordering = ['idxIapo__BarcoPS','-idxIapo__numPS']  

    def __str__(self):
        return f"{self.idxIapo}"

    def save(self, *args, **kwargs):
        """Calcula os três domingos automaticamente"""
        if self.idxIapo and self.idxIapo.dataEmissaoPS:
            data_base = self.idxIapo.dataEmissaoPS
            
            # Achar próximo domingo
            dias_ate_domingo = (6 - data_base.weekday()) % 7
            if dias_ate_domingo == 0:  
                dias_ate_domingo = 7
            
            primeiro_domingo = data_base + timedelta(days=dias_ate_domingo)
            
            # Calcular os três domingos
            self.priDomIapo = primeiro_domingo
            self.segDomIapo = primeiro_domingo + timedelta(weeks=1)
            self.terDomIapo = primeiro_domingo + timedelta(weeks=2)

            print(f"priDomIapo: {self.priDomIapo}")
            print(f"segDomIapo: {self.segDomIapo}")
            print(f"terDomIapo: {self.terDomIapo}")
        
        super().save(*args, **kwargs)



#-==========================================================4.2 SMS===================================================
#===========================================================4.2.1 LV de Mangueiras====================================

class smsLvMang(models.Model):
    """Modelo para cadastro de Passagem de Serviço - LV de Mangueiras - SMS"""

    idxsmsLvMang = models.ForeignKey(PassServ, on_delete=models.CASCADE)

    dataUltLvMang = models.DateField(verbose_name='Data da Última LV')
    dataProxLvMang = models.DateField(verbose_name='Data da Próxima LV')
    obsLvMang = models.TextField(max_length=500, verbose_name='Observações', blank=True)

    class Meta:
        verbose_name = 'LV de Mangueiras'
        verbose_name_plural = 'LVs de Mangueiras'
        ordering = ['idxsmsLvMang__BarcoPS','-idxsmsLvMang__numPS']  

    def __str__(self):
        return f"{self.idxsmsLvMang} - {self.dataProxLvMang}"
    
    def save(self, *args, **kwargs):
        """Calcula automaticamente a próxima LV (60 dias após a última)"""
        if self.dataUltLvMang:
            self.dataProxLvMang = self.dataUltLvMang + timedelta(days=60)
            
        
        super().save(*args, **kwargs)
        


#===========================================================4.2.2 LV de Segurança====================================

class smsLvSeg(models.Model):
    """Modelo para cadastro de Passagem de Serviço - LV de Segurança - SMS"""

    idxsmsLvSeg = models.ForeignKey(PassServ, on_delete=models.CASCADE)

    LvSegCamoAsogUlt = models.DateField(verbose_name='Data da Última LV CAMO/ASOG')
    LvSegCamoAsogProx = models.DateField(verbose_name='Data da Próxima LV CAMO/ASOG')
    LvlSegCamoAsogFarol = models.CharField(max_length=3,verbose_name='Farol LV CAMO/ASOG')
    LvSegCondNavioCpUlt = models.DateField(verbose_name='Data da Última LV Condição Navio(Curto Prazo)')  
    LvSegCondNavioCpProx = models.DateField(verbose_name='Data da Próxima LV Condição Navio(Curto Prazo)') 
    LvSegCondNavioCpFarol = models.DateField(verbose_name='Farol LV Condição Navio(Curto Prazo)')
    LvlSegCondNavioLpUlt = models.DateField(verbose_name='Data da Última LV Condição Navio(Longo Prazo)')  
    LvSegCondNavioLpProx = models.DateField(verbose_name='Data da Próxima LV Condição Navio(Longo Prazo)') 
    LvSegCondNavioLpFarol = models.DateField(verbose_name='Farol LV Condição Navio(Longo Prazo)') 
    LvSegEspConfUlt = models.DateField(verbose_name='Data da Última LV Espaço Confinado')
    LvSegEspConfProx = models.DateField(verbose_name='Data da Próxima LV Espaço Confinado')
    LvSegEspConfFarol = models.CharField(max_length=3,verbose_name='Farol LV Espaço Confinado')
    LvSegMovCargasUlt = models.DateField(verbose_name='Data da Última LV Movimentação de Cargas')
    LvSegMovCargasProx = models.DateField(verbose_name='Data da Próxima LV Movimentação de Cargas')
    LvSegMovCargasFarol = models.CharField(max_length=3,verbose_name='Farol LV Movimentação de Cargas') 
    LvSegPintQuimPerUlt = models.DateField(verbose_name='Data da Última LV Pintura e Produtos Químicos Perigosos')
    LvSegPintQuimPerProx = models.DateField(verbose_name='Data da Próxima LV Pintura e Produtos Químicos Perigosos')
    LvSegPintQuimPerFarol = models.CharField(max_length=3,verbose_name='Farol LV Pintura e Produtos Químicos Perigosos')
    LvSegProcVcpUlt = models.DateField(verbose_name='Data da Última LV de Processo de VCP')
    LvSegProcVcpProx = models.DateField(verbose_name='Data da Próxima LV de Processo de VCP')
    LvSegProcVcpFarol = models.CharField(max_length=3,verbose_name='Farol LV de Processo de VCP')
    LvlSegRespEmergUlt = models.DateField(verbose_name='Data da Última LV de Resposta a Emergência')
    LvSegRespEmergProx = models.DateField(verbose_name='Data da Próxima LV de Resposta a Emergência')
    LvSegRespEmergFarol = models.CharField(max_length=3,verbose_name='Farol LV de Resposta a Emergência')
    LvlSegRiscSanitUlt = models.DateField(verbose_name='Data da Última LV de Risco Sanitário')
    LvSegRiscSanitProx = models.DateField(verbose_name='Data da Próxima LV de Risco Sanitário')
    LvSegRiscSanitFarol = models.CharField(max_length=3,verbose_name='Farol LV de Risco Sanitário')
    LvSegTestHidrostUlt = models.DateField(verbose_name='Data da Última LV de Teste Hidrostático')
    LvSegTestHidrostProx = models.DateField(verbose_name='Data da Próxima LV de Teste Hidrostático')
    LvSegTestHidrostFarol = models.CharField(max_length=3,verbose_name='Farol LV de Teste Hidrostático')
    LvlSegTrabQuentUlt = models.DateField(verbose_name='Data da Última LV de Trabalho a Quente')
    LvSegTrabQuentProx = models.DateField(verbose_name='Data da Próxima LV de Trabalho a Quente')
    LvSegTrabQuentFarol = models.CharField(max_length=3,verbose_name='Farol LV de Trabalho a Quente')
    LvlSegTrabAltUlt = models.DateField(verbose_name='Data da Última LV de Trabalho em Altura')
    LvSegTrabAltProx = models.DateField(verbose_name='Data da Próxima LV de Trabalho em Altura')
    LvSegTrabAltFarol = models.CharField(max_length=3,verbose_name='Farol LV de Trabalho em Altura')
    LvlSegTrabEletrUlt = models.DateField(verbose_name='Data da Última LV de Trabalho em eletricidade')
    LvSegTrabEletrProx = models.DateField(verbose_name='Data da Próxima LV de Trabalho em eletricidade')
    LvSegTrabEletrFarol = models.CharField(max_length=3,verbose_name='Farol LV de Trabalho em eletricidade')
    obsLvSeg = models.TextField(max_length=500, verbose_name='Observações', blank=True)

    class Meta:
        verbose_name = 'LV de Segurança'
        verbose_name_plural = 'LVs de Segurança'
        ordering = ['idxsmsLvSeg__BarcoPS','-idxsmsLvSeg__numPS']  

    def __str__(self):
        return f"{self.idxsmsLvSeg}"
    
    def save(self, *args, **kwargs):
        """Irá capturar os dados de uma outra aplicação futuramente"""
        pass
        super().save(*args, **kwargs)
        




















