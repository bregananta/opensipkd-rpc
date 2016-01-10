import sys
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    String,
    SmallInteger,
    types,
    func
    )

from sqlalchemy.orm.exc import NoResultFound

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    backref
    )
import re
            
KECAMATAN = [
    ('kd_propinsi', 2, 'N'),
    ('kd_dati2', 2, 'N'),
    ('kd_kecamatan', 3, 'N'),]
    
DESA = [
    ('kd_propinsi', 2, 'N'),
    ('kd_dati2', 2, 'N'),
    ('kd_kecamatan', 3, 'N'),
    ('kd_kelurahan', 3, 'N'),]

NOP = [
    ('kd_propinsi', 2, 'N'),
    ('kd_dati2', 2, 'N'),
    ('kd_kecamatan', 3, 'N'),
    ('kd_kelurahan', 3, 'N'),
    ('kd_blok', 3, 'N'),
    ('no_urut', 4, 'N'),
    ('kd_jns_op', 1, 'N'),]
    
from ..tools import as_timezone, FixLength

from ..models import CommonModel, pbb_Base, pbb_DBSession

class Propinsi(pbb_Base, CommonModel):
    __tablename__  = 'ref_propinsi'
    __table_args__ = {'extend_existing':True, 'autoload':True}

class Dati2(pbb_Base, CommonModel):
    __tablename__  = 'ref_dati2'
    __table_args__ = {'extend_existing':True, 'autoload':True}

class Kecamatan(pbb_Base, CommonModel):
    __tablename__  = 'ref_kecamatan'
    __table_args__ = {'extend_existing':True, 'autoload':True}

class Kelurahan(pbb_Base, CommonModel):
    __tablename__  = 'ref_kelurahan'
    __table_args__ = {'extend_existing':True, 'autoload':True}

class DatObjekPajak(pbb_Base, CommonModel):
    __tablename__  = 'dat_objek_pajak'
    __table_args__ = {'extend_existing':True, 'autoload':True}
    @classmethod
    def query_data(cls):
        return pbb_DBSession.query(cls)
        
    @classmethod
    def get_by_nop(cls, p_kode):
        pkey = FixLength(NOP)
        pkey.set_raw(p_kode)
        query = cls.query_data()
        return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            kd_dati2 = pkey['kd_dati2'], 
                            kd_kecamatan = pkey['kd_kecamatan'], 
                            kd_kelurahan = pkey['kd_kelurahan'], 
                            kd_blok = pkey['kd_blok'], 
                            no_urut = pkey['no_urut'], 
                            kd_jns_op = pkey['kd_jns_op'],)

class DatSubjekPajak(pbb_Base, CommonModel):
    __tablename__  = 'dat_subjek_pajak'
    __table_args__ = {'extend_existing':True, 'autoload':True}
    
class Sppt(pbb_Base, CommonModel):
    __tablename__  = 'sppt'
    __table_args__ = {'extend_existing':True, 'autoload':True}
    
    @classmethod
    def query_data(cls):
        return pbb_DBSession.query(cls)
        
    @classmethod
    def get_by_nop(cls, p_kode):
        pkey = FixLength(NOP)
        pkey.set_raw(p_kode)
        query = cls.query_data()
        return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            kd_dati2 = pkey['kd_dati2'], 
                            kd_kecamatan = pkey['kd_kecamatan'], 
                            kd_kelurahan = pkey['kd_kelurahan'], 
                            kd_blok = pkey['kd_blok'], 
                            no_urut = pkey['no_urut'], 
                            kd_jns_op = pkey['kd_jns_op'],)
    @classmethod
    def get_nop_by_nop_thn(cls, p_kode, p_tahun):
        query = cls.get_by_nop(p_kode)
        return query.filter_by(thn_pajak_sppt = p_tahun)
        
    @classmethod
    def get_nop_by_kelurahan(cls, p_kode, p_tahun):
        pkey = FixLength(DESA)
        pkey.set_raw(p_kode)
        query = cls.query_data()
        return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            kd_dati2 = pkey['kd_dati2'], 
                            kd_kecamatan = pkey['kd_kecamatan'], 
                            kd_kelurahan = pkey['kd_kelurahan'], 
                            thn_pajak_sppt = p_tahun)
                            
    @classmethod
    def get_nop_by_kecamatan(cls, p_kode, p_tahun):
        pkey = FixLength(KECAMATAN)
        pkey.set_raw(p_kode)
        query = cls.query_data()
        return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            kd_dati2 = pkey['kd_dati2'], 
                            kd_kecamatan = pkey['kd_kecamatan'], 
                            kd_kelurahan = pkey['kd_kelurahan'], 
                            thn_pajak_sppt = p_tahun)
                            
    @classmethod
    def get_rekap_desa(cls, p_kode, p_tahun):
        pkey = FixLength(KECAMATAN)
        pkey.set_raw(p_kode)
        query = pbb_DBSession.query(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan, cls.kd_kelurahan, 
                               func.sum(cls.pbb_yg_harus_dibayar_sppt).label('tagihan')).\
                               group_by(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan, cls.kd_kelurahan)
        return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            kd_dati2 = pkey['kd_dati2'], 
                            kd_kecamatan = pkey['kd_kecamatan'], 
                            thn_pajak_sppt = p_tahun)

    @classmethod
    def get_rekap_kec(cls, p_tahun):
        query = pbb_DBSession.query(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan,  
                               func.sum(cls.pbb_yg_harus_dibayar_sppt).label('tagihan')).\
                               group_by(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan)
        return query.filter_by(thn_pajak_sppt = p_tahun)

    @classmethod
    def get_info_op(cls, p_kode):
        pkey = FixLength(NOP)
        pkey.set_raw(p_kode)
        query = pbb_DBSession.query(
              func.concat(cls.kd_propinsi, '.').concat(cls.kd_dati2).concat('-').\
                   concat(cls.kd_kecamatan).concat('.').concat(cls.kd_kelurahan).concat('-').\
                   concat(cls.kd_blok).concat('.').concat(cls.no_urut).concat('-').\
                   concat(cls.kd_jns_op).label('nop'),
              func.concat(DatObjekPajak.jalan_op,', ').concat(DatObjekPajak.blok_kav_no_op).label('alamat_op'),
              func.concat(DatObjekPajak.rt_op,' / ').concat(DatObjekPajak.rw_op).label('rt_rw_op'),
              DatObjekPajak.total_luas_bumi, DatObjekPajak.total_luas_bng, cls.nm_wp_sppt.label('nm_wp'),
              func.concat(cls.jln_wp_sppt,', ').concat(cls.blok_kav_no_wp_sppt).label('alamat_wp'),
              func.concat(cls.rt_wp_sppt, ' / ').concat(cls.rw_wp_sppt).label('rt_rw_wp'),
              cls.kelurahan_wp_sppt.label('kelurahan_wp'), cls.kota_wp_sppt.label('kota_wp'), 
              cls.thn_pajak_sppt, cls.luas_bumi_sppt.label('luas_tanah'), cls.njop_bumi_sppt.label('njop_tanah'),
              cls.luas_bng_sppt.label('luas_bng'),cls.njop_bng_sppt.label('njop_bng'),
              cls.pbb_yg_harus_dibayar_sppt.label('ketetapan'), cls.status_pembayaran_sppt.label('status_bayar')
              ).outerjoin(DatObjekPajak).filter(cls.kd_propinsi == DatObjekPajak.kd_propinsi, 
                            cls.kd_dati2 == DatObjekPajak.kd_dati2, 
                            cls.kd_kecamatan == DatObjekPajak.kd_kecamatan, 
                            cls.kd_kelurahan == DatObjekPajak.kd_kelurahan, 
                            cls.kd_blok == DatObjekPajak.kd_blok, 
                            cls.no_urut == DatObjekPajak.no_urut, 
                            cls.kd_jns_op == DatObjekPajak.kd_jns_op,)
        return query.filter(cls.kd_propinsi == pkey['kd_propinsi'], 
                            cls.kd_dati2 == pkey['kd_dati2'], 
                            cls.kd_kecamatan == pkey['kd_kecamatan'], 
                            cls.kd_kelurahan == pkey['kd_kelurahan'], 
                            cls.kd_blok == pkey['kd_blok'], 
                            cls.no_urut == pkey['no_urut'], 
                            cls.kd_jns_op == pkey['kd_jns_op'],)
        
class PembayaranSppt(pbb_Base, CommonModel):
    __tablename__  = 'pembayaran_sppt'
    __table_args__ = {'extend_existing':True, 'autoload':True}
    
    @classmethod
    def query_data(cls):
        return pbb_DBSession.query(cls)
        
    @classmethod
    def get_by_nop(cls, p_nop):
        pkey = FixLength(NOP)
        pkey.set_raw(p_nop)
        query = cls.query_data()
        return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            kd_dati2 = pkey['kd_dati2'], 
                            kd_kecamatan = pkey['kd_kecamatan'], 
                            kd_kelurahan = pkey['kd_kelurahan'], 
                            kd_blok = pkey['kd_blok'], 
                            no_urut = pkey['no_urut'], 
                            kd_jns_op = pkey['kd_jns_op'],)
    @classmethod
    def get_nop_by_nop_thn(cls, p_nop, p_tahun):
        query = cls.get_by_nop(p_nop)
        return query.filter_by(thn_pajak_sppt = p_tahun)
        
    @classmethod
    def get_nop_by_kelurahan(cls, p_kode, p_tahun):
        pkey = FixLength(DESA)
        pkey.set_raw(p_kode)
        query = cls.query_data()
        return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            kd_dati2 = pkey['kd_dati2'], 
                            kd_kecamatan = pkey['kd_kecamatan'], 
                            kd_kelurahan = pkey['kd_kelurahan'], 
                            thn_pajak_sppt = p_tahun)
                            
    @classmethod
    def get_nop_by_kecamatan(cls, p_kode, p_tahun):
        pkey = FixLength(KECAMATAN)
        pkey.set_raw(p_kode)
        query = cls.query_data()
        return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            kd_dati2 = pkey['kd_dati2'], 
                            kd_kecamatan = pkey['kd_kecamatan'], 
                            kd_kelurahan = pkey['kd_kelurahan'], 
                            thn_pajak_sppt = p_tahun)
    
    @classmethod
    def get_nop_by_tanggal(cls, p_kode, p_tahun):
        pkey = DateVar
        p_kode = re.sub("[^0-9]", "", p_kode)
        pkey.set_raw(p_kode)
        query = cls.query_data()
        return query.filter_by(tgl_pembayaran_sppt = pkey.get_value)
                            
    @classmethod
    def get_rekap_desa(cls, p_kode, p_tahun):
        pkey = FixLength(KECAMATAN)
        pkey.set_raw(p_kode)
        query = pbb_DBSession.query(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan, cls.kd_kelurahan, 
                               func.sum(cls.denda_sppt).label('denda'),
                               func.sum(cls.pbb_yg_dibayar_sppt).label('jumlah') ).\
                               group_by(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan, cls.kd_kelurahan)
        return query.filter_by(kd_propinsi = pkey['kd_propinsi'], 
                            kd_dati2 = pkey['kd_dati2'], 
                            kd_kecamatan = pkey['kd_kecamatan'], 
                            thn_pajak_sppt = p_tahun)

    @classmethod
    def get_rekap_kec(cls, p_tahun):
        query = pbb_DBSession.query(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan,  
                               func.sum(cls.denda_sppt).label('denda'),
                               func.sum(cls.pbb_yg_dibayar_sppt).label('jumlah')).\
                               group_by(cls.kd_propinsi, cls.kd_dati2, cls.kd_kecamatan)
        return query.filter_by(thn_pajak_sppt = p_tahun)
                                     