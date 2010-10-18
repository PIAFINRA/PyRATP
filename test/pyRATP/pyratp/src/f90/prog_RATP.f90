module RATP

 use constant_values
 use grid3D
 use skyvault
 use vegetation_types
 use dir_interception
 use hemi_interception
 use shortwave_balance
 use micrometeo
 use energy_balance
 use Photosynthesis
 use MinerPheno

 integer :: numx_out(100), numy_out(100), numz_out(100), kxyz_out(100)
 integer ::  form_vgx=55
 integer :: fileTypeArchi = 1
 integer :: val = 1
 character*200 fname



 character(len=28):: fnameGrid3D
 character(len=28):: fnameVegetation
 character(len=28):: fnameMeteo
 character(len=28):: fnameSkyVault
 character(len=28):: fnameDigital
 character(len=28):: fnameVegestar


 character(len=100):: pathGrid3D
 character(len=17):: pathVegetation
 character(len=17):: pathMeteo
 character(len=100):: pathSkyVault
 character(len=100):: pathDigital
 character(len=17):: pathResult

 integer :: nbvoxelveg = 1
 integer :: nbiter = 0
 integer :: numfichmeteo = 0

 character*2 hhx, hhy, hhz
contains
!----------------------------

 !subroutine do_all(x,y,z)
 !  real, intent(in) :: x,y
 !  real, intent(out) :: z
 subroutine do_all


 !write(*,*)
 !write(*,*)  ' R. A. T. P.    Version 2.0'
 !write(*,*)  ' Radiation Absorption, Transpiration and Photosynthesis'
 !write(*,*)
 !write(*,*)  ' Spatial distribution in a 3D grid of voxels'
 !write(*,*)
 !write(*,*)  '                July 2003'
 !write(*,*)

 !write(*,*)
 !write(*,*)

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! spec_grid='grd'     ! definition de la grille
! spec_vegetation='veg'   ! definition des types de végétation

! spec_gfill='dgi'     ! definition du fichier de structure (feuillage)
!spec_mmeteo='mto'     ! definition du fichier mmeteo
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

 call cv_set

 write(*,*) 'Lecture fichier Grille'
 call g3d_read(fnameGrid3D)
 write(*,*) 'Remplissage de la Grille'
 call g3d_fill(fnameDigital,fileTypeArchi ,pathResult)  !Option remplissage: 1: fichier de feuilles (digital.xxx); 2: fichier de voxels (leafarea.xxx)
 !pause

! sorties VegeSTAR--------------------------------------------------------------------------------
 write(*,*) 'Ecriture fichier VegeSTAR'
 fname = pathResult//'sortieVegeSTAR.vgx'
 open (16,file=fname)
 write(16,*) 'Obj EchX EchY EchZ TransX TransY TransZ RotX RotY RotZ R G B'
 nbvoxelveg = nveg
 do k=1,nveg
  if (((numy(k)-1)*dy).ge.(yrang/2)) then
   write(16,100) form_vgx,dx,dy,dz(numz(k)),(numx(k)-1)*dx,(numy(k)-1)*dy-yrang,(numz(k)-1)*dz(numz(k)),0,0,0,0,255,0
  else
   write(16,100) form_vgx,dx,dy,dz(numz(k)),(numx(k)-1)*dx,(numy(k)-1)*dy,(numz(k)-1)*dz(numz(k)),0,0,0,255,0,0
  end if
 end do
100 format(1x,i2,6(1x,f6.3),6(1x,i3))
 close(16)
!fin sorties VegeSTAR--------------------------------------------------------------------------------
 z = sin(x+y)
 write(*,*) 'Lecture fichier Skyvault'
!  skyvault--------------------------------------------------------------------------------
! fname='skyvault.'//spec
 call sv_read(fnameSkyVault)
!  fin skyvault--------------------------------------------------------------------------------
 write(*,*) 'Lecture fichier Vegetation'
! fname='vegetation.'//spec
 call vt_read(nent,pathVegetation,fnameVegetation)
! pause

 dpx=dx/5.
 dpy=dy/5.


 scattering=.FALSE.
 isolated_box=.FALSE.

! call Farquhar_parameters_set

 call hi_doall(dpx,dpy,isolated_box)  ! Compute interception of diffuse and scattering radiation, ie exchange coefficients

! Running several files mmeteo in a sequence
! The list of file suffixes is given in file mmeteofilenames.txt

!
! Ouverture du fichier contenant le nom des fichiers mmeteo


 open(15,file=fnameMeteo)

 !do while (.NOT.eof(15))
 !read(15,*) spec_mmeteo
 write(*,*) 'Lecture fichier meteo'
 do while (.true.)
 read(15,*,end = 999) spec_mmeteo
 numfichmeteo = numfichmeteo + 1
 fname=pathResult//'output_PARclasses.'//spec_mmeteo
 open (2,file=fname)
 write(2,*) 'ntime day hour vt PARg %SF50 %SF100'

 fname=pathResult//'output_tsclasses.'//spec_mmeteo
 open (3,file=fname)
 write(3,*) 'ntime day hour vt Tair %SF11 %SF12'

 fname=pathResult//'output_minerpheno.'//spec_mmeteo
 open (10,file=fname)
 write(10,*) 'ntime day hour sumTair Nlarvaout Nlarvadead Tair'

! Leaf temperature at the voxel scale

 fname = pathResult//'output_leafTemp.'//spec_mmeteo
 open (12,file=fname)
 write(12,*) 'ntime day hour voxel Tsh Tshm Tsl Tslm Tair Tbody(10xx mort,+50xx out)'


! Memory allocation in MinerPheno module
 call miph_destroy
 call miph_allocate ! includes Variable initiation to 0

 ntime=0
 endmeteo=.FALSE.
 do while (.NOT.((endmeteo).OR.((nlarvaout+nlarvadead).ge.voxel_canopy(2))))
  ntime=ntime+1
  write(*,*) 'Fichier meteo :',numfichmeteo,'...Iteration : ',ntime
  call mm_read(ntime,pathMeteo,spec_mmeteo)  ! Read micrometeo data (line #ntime in file mmeteo.<spec>)
  call swrb_doall     ! Compute short wave radiation balance
  call eb_doall_mine    ! Compute energy balance
  call miph_doall     ! Compute miner larva development

  do jent=1,nent
   write(2,20) ntime, day, hour, jent, glob(1)*2.02/0.48, (Spar(jent,class)/S_vt(jent), class=1,45) ! %SF per irradiance class
   write(3,30) ntime, day, hour, jent, taref, (Sts(jent,class)/S_vt(jent), class=10,45)
  end do

  write(10,70) ntime, day, hour, sum_taref, Nlarvaout, Nlarvadead, taref, sum_dev_rate(1), sum_dev_rate(10), sum_dev_rate(100)

  !if (hour.eq.12) then
  do k=1,nveg
   do je=1,nje(k)
     jent=nume(je,k)
     if (ismine(jent).eq.1) then
      if (larvadeath(k).gt.0) then
       write(12,90) ntime, day, hour, k, ts(0,1,k), ts(0,2,k), ts(1,1,k), ts(1,2,k), taref, 1000 + ntime + .0
      else if  (larvaout(k).gt.0) then
       write(12,90) ntime, day, hour, k, ts(0,1,k), ts(0,2,k), ts(1,1,k), ts(1,2,k), taref, 5000 + ntime + .0
      else
       write(12,90) ntime, day, hour, k, ts(0,1,k), ts(0,2,k), ts(1,1,k), ts(1,2,k), taref, tbody(k)
      end if
     end if
   end do
  end do
  !end if
 end do

 nbiter =nbiter + ntime

! close (1)
 close (2)
 close (3)
 close (10)
 close (12)

! Mine phenology at voxel scale, at the end of the simulation period

 fname = pathResult//'output_minerspatial.'//spec_mmeteo
 open (11,file=fname)
 write(11,*) 'Voxel# jx jy jz time_death time_out sum_tair_out'




 do k=1,nveg
  if (sum_dev_rate(k).gt.0.) then   ! Voxel k includes a miner
   write(11,80) k, numx(k), numy(k), numz(k), larvadeath(k), larvaout(k), sum_tair(k)
  endif
 end do

 close (11)

 end do  ! next mmeteo file
 999 continue

 close (15)


 !pause

10 format(i4,1x,f4.0,1x,f5.2,2(1x,f5.3),2(1x,f7.3))
11 format(i4,1x,f4.0,1x,f5.2,12(1x,f7.3))
12 format(i4,1x,f4.0,1x,f6.3,10(1x,i2,1x,2(f6.2,1x),2(f6.0,1x),2(f9.6,1x)))
20 format(i4,1x,f4.0,1x,f6.2,1x,i2,1x,f5.0,50(1x,f8.6))
30 format(i4,1x,f4.0,1x,f6.2,1x,i2,1x,f6.2,50(1x,f5.3))
70 format(i4,1x,f4.0,1x,f6.2,1x,f9.0,2(1x,i5),1x,f6.2,3(1x,f6.4))
80 format(i5,1x,3(i3,1x),2(i4,1x),f8.1)
90 format(i4,1x,f4.0,1x,f6.2,1x,i5,6(1x,f8.3))


! Deallocation des tableaux

 call g3d_destroy
 call sv_destroy
 call vt_destroy
 call mm_destroy
 call di_destroy
 call hi_destroy
 call swrb_destroy
 call eb_destroy
 call ps_destroy
 call miph_destroy

 !pause
 !z = sin(x+y)
 write(*,*) 'CALCULS TERMINES'
 end subroutine do_all

end module RATP

