# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 14:29:13 2017

@author: haiau
"""

import math
import numpy as np
import scipy.special as scs
import QuadElement as qa
import FEMBoundary as FB
#import warnings

class AxisymmetricQuadElement(qa.QuadElement):
    """
    Axisymmetric Quadrilateral Element
    """
    def __init__(self, Nodes, pd, basisFunction, nodeOrder, material, intData):
        """
        Initialize an Axisymmetric Element
        Input:
            Nodes: nodes of elements
            pd: basis function degree(s),
                if number of dimension == 1, pd is an integer
                else, pd is an list
            basisFunction: basis function, see super class info
            nodeOrder: the order of nodes in elements,
            for 1 dimensional element, nodeOrder is an increasing array,
            for >1 dimensional elelement, nodeOrder is a n-dim-array
            material: material of element
            intData: integration data
        Raise:
            DimensionMismatch: if dimensions in Nodes is not equal 2
        """
        for node in Nodes:
            if node.getNdim() != 2:
                raise DimensionMismatch
                
        qa.QuadElement.__init__(self,Nodes,pd,basisFunction,\
        nodeOrder,material,intData)
        
    def getFactor(self):
        """
        Return: factor for integration, 2*pi*radius*det(J)
        """
        return 2*np.pi*self.x_[0]*self.factor[self.ig]
        
class AxisymmetricStaticBoundary(FB.StandardStaticBoundary):
    """
    Boundary of Axisymmetric element that is not moving during simulation
    """
    def calculateGreen(self, x, xp):
        if np.allclose(x,xp,rtol=1.0e-13) or math.fabs(xp[0])<1.0e-14:
            raise FB.SingularPoint
        r = x[0]
        rp = xp[0]
        z = x[1]
        zp = xp[1]
        
        mt = (z-zp)**2 + (r+rp)**2
        m = 4*r*rp/mt
        self.G = 0.0
        self.gradG[0] = 0.0
        self.gradG[1] = 0.0
        mt = math.sqrt(mt)*np.pi
        kint = scs.ellipk(m)
        eint = scs.ellipe(m)
            
        
        if np.isnan(kint) or np.isnan(eint):
            raise Exception('False elliptic integral m = '+str(m))
        self.G = rp*((2.0-m)*kint-2.0*eint)/(m*mt)
        self.gradG[0] = r*(2.0*m-4.0)*kint
        self.gradG[0] += r*(m*m-8.0*m+8.0)/(2.0*(1.0-m))*eint
        self.gradG[0] += rp*m*kint
        self.gradG[0] -= rp*m*(2.0-m)/(2.0*(1.0-m))*eint
        self.gradG[0] /= (math.sqrt(m)*(math.sqrt(r*rp)**3))
        self.gradG[0] *= rp/(4.0*np.pi)
        
        self.gradG[1] = (2.0-m)/(1.0-m)*eint - 2.0*kint
        self.gradG[1] *= math.sqrt(m)*(z-zp)/(2.0*math.sqrt(r*rp)**3)
        self.gradG[1] *= rp/(4.0*np.pi)
            #raise Exception('False elliptic integral')
        
    def postCalculateF(self, N_, dN_, factor, res):
        r = self.x_[0]
        k1 = self.u_[0]*\
        (self.normv[0]*self.gradG[0]+self.normv[1]*self.gradG[1])
        k1 *= factor
        k1 += self.u_[0]*self.G*self.normv[0]*factor/r
        k2 = self.u_[1]*self.G
        k2 *= factor
        res += k1 + k2
        
    def subCalculateKLinear(self, K, element, i, j):
        #if np.allclose(element.xx_[0],0.0,rtol = 1.0e-14):
        #    K.fill(0.0)
        #    return
        wfac = self.getFactor()
        wfact = element.getFactorX(element.detJ)
        wfacx = element.getFactorXR(element.detJ)
        K[1,0] = self.N_[i]*element.Nx_[j]*\
        (element.normv[0]*self.gradG[0]+element.normv[1]*self.gradG[1])
        K[1,0] *= wfac*wfacx
        K[1,0] += self.N_[i]*element.Nx_[j]*self.G*\
        element.normv[0]*wfac*wfact/element.xx_[0]
        K[1,1] = self.N_[i]*element.Nx_[j]*self.G
        K[1,1] *= wfac*wfact
        
#    def subCalculateR(self, R, element, i):
#        #if np.allclose(element.xx_[0],0.0,rtol = 1.0e-14):
#        #    return
#        wfac = self.getFactor()
#        wfact = element.getFactorX(element.detJ)
#        wfacx = element.getFactorXR(element.detJ)
#        r0 = self.N_[i]*element.ux_[0]*\
#        (element.normv[0]*self.gradG[0]+element.normv[1]*self.gradG[1])
#        r0 *= wfac*wfacx
#        r0 += self.N_[i]*element.ux_[0]*self.G*\
#        element.normv[0]*wfac*wfact/element.xx_[0]
#        r1 = self.N_[i]*element.ux_[1]*self.G
#        r1 *= wfac*wfact
#        R[1] += (r0 + r1)
                
        
class DimensionMismatch(Exception):
    """
    Exception for dimensions in node and element do not match
    """
    pass