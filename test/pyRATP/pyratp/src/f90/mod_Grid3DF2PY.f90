!------------------------------------------------------------------------------

module grid3D

character*6	spec_grid		! for grid 3D definition
character*6	spec_gfill		! canopy structure for grid filling

!  EMPTY grid
integer :: njx, njy, njz    ! number of grid voxels along X Y and Z axis
real  :: dx, dy       ! voxel size according to X- and Y- axis
real, allocatable :: dz(:)    ! voxel size according to  Z- axis
real  :: xorig, yorig, zorig   ! 3D grid origin
real  :: latitude, longitude, timezone
real  :: orientation     ! angle (°) between axis X+ and North
integer :: idecaly                  ! offset between canopy units along Y-axis

! Soil surface
integer :: nsol       ! number of soil surface cells
integer :: nblosoil     ! Number of wavelength bands for the soil surface
real, allocatable    :: rs(:)      ! Soil reflectance in PAR and NIR bands
real :: total_ground_area   ! Total ground area of the scene


!   VEGETATED grid
integer :: nveg       ! number of vegetated voxels
integer :: nent       ! number of vegetation types in the 3D grid
integer :: nemax       ! maximum number of vegetation types in a voxel (nemax < nent)

real, allocatable :: S_vt_vx(:,:) ! Leaf area (m²) per voxel and vegetation type
real, allocatable :: S_vx(:)       ! Leaf area (m²) per voxel
real, allocatable :: S_vt(:)    ! Leaf area (m²) per vegetation type
real ::      S_canopy        ! Leaf area (m²) of canopy (ex-variable sft)

real, allocatable :: volume_canopy(:)  ! cumulative volume (m3) of vegetated voxels, for each vegetation type, index nent+1 for total canopy volume
integer, allocatable :: voxel_canopy(:)  ! number of vegetated voxels, for each vegetation type
real :: N_canopy   ! average nitrogen content (g m-2)

integer, allocatable :: kxyz(:,:,:)  ! voxel index (as a function of location in the 3D grid)
integer, allocatable :: numx(:)   ! voxel x-coordinate (as a function of voxel #)
integer, allocatable :: numy(:)   ! voxel y-coordinate (as a function of voxel #)
integer, allocatable :: numz(:)   ! voxel z-coordinate (as a function of voxel #)
integer, allocatable :: nje(:)   ! number of vegetation types in voxel (as a function of voxel #)


integer, allocatable :: nume(:,:)   ! type # of each vegetation type in each voxel
real, allocatable    :: leafareadensity(:,:)   ! leaf area density of each vegetation type in each voxel
real, allocatable    :: N_detailed(:,:)   ! nitrogen content (g m-2) of each vegetation type in each voxel


contains
   subroutine g3d_read(fname)

  !character*6 spec
  character*28 fname

  !write(*,*) 'Creating the empty 3D grid from input file ...',fname
  !write(*,*)

  call g3d_destroy

!  Reading the input file

  !fname='grid3D.'//spec
  open (1,file=fname)
  read(1,*) njx, njy, njz      ! number of grid voxels along X Y and Z axis
  allocate(dz(njz+1))       ! allocated to (njz+1) as needed in beampath
  read(1,*) dx, dy, (dz(jz),jz=1,njz)  ! voxel size according to X- Y- and Z- axis
  read(1,*) xorig, yorig, zorig    ! 3D grid origin
  read(1,*) latitude, longitude, timezone
  read(1,*) orientation      ! angle (°) between axis X+ and North
  read(1,*) idecaly        ! offset between canopy units along Y-axis
!      idecaly <> 0 : plantation en quinconce partiel (ie, decalage des Y
!      d'un nombre entier idecaly de cellules Y d'une maille a l'autre).
!             si idecaly = njy / 2 : quinconce parfait
!             si idecaly = 0       : plantation orthogonale
!      Cf. Subroutine Beampath

  read(1,*) nent     ! nent: number of vegetation types in the 3D grid

  !read(1,*) nblosoil   ! number of wavelength bands for the soil surface
  !allocate(rs(nblosoil))
  !backspace (1)
  !read(1,*) nblosoil, (rs(iblo),iblo=1,nblosoil) ! soil reflectance for each wave

  allocate(rs(2))
  nblosoil = 2
  rs(1) = 0.075
  rs(2) = 0.2
  close (1)

  nvegmax=njx*njy*njz

  xrang=real(njx)*dx
  yrang=real(njy)*dy
  total_ground_area=xrang*yrang

! Allocation of allocatable arrays:
! In a first approximation, most arrays are over-allocated to NENT and NVEGMAX

  allocate(kxyz(njx,njy,njz+1))
  allocate(numx(nvegmax), numy(nvegmax), numz(nvegmax), nje(nvegmax))

  allocate(leafareadensity(nent,nvegmax), N_detailed(nent,nvegmax))
  allocate(nume(nent,nvegmax))

  allocate(S_vt_vx(nent,nvegmax)) ! Leaf area (m²) per voxel and vegetation type
  allocate(S_vx(nvegmax))        ! Leaf area (m²) per voxel
  allocate(S_vt(nent))      ! Leaf area (m²) per vegetation type
  allocate(volume_canopy(nent+1))
  allocate(voxel_canopy(nent))

  volume_canopy=0.
  voxel_canopy=0

  kxyz=0
  numx=0
  numy=0
  numz=0
  nje=0
  nume=0
  leafareadensity=0.
  N_detailed=0.

   end subroutine g3d_read

!*******************************
   subroutine g3d_create(njx_i, njy_i, njz_i, size_x, size_y, size_z)

  integer :: njx_i, njy_i, njz_i
  real  :: size_x, size_y, size_z

  !write(*,*) 'Creating the empty 3D grid from box size and division info ...'
  !write(*,*) 'rem: other parameters are set to default values'
  !write(*,*)

  call g3d_destroy

  njx = njx_i       ! number of grid voxels along X Y and Z axis
  njy = njy_i
  njz = njz_i

  dx = size_x / float(njx)  ! voxel size according to X- Y- and Z- axis
  dy = size_y / float(njy)
  allocate(dz(njz+1))     ! allocated to (njz+1) as needed in beampath
  do jz=1,njz
   dz(jz)= size_z / float(njz) ! all Z-layers are assumed to have the same depth
  end do

!  Default values of other parameters

  xorig = 0.    ! 3D grid origin
  yorig = 0.
  zorig = 0.

  latitude = 45.  ! latitude  (°)
  longitude = 0.  ! longitude (°)
  timezone= -2.  ! summer time in France (-2 hours)

  orientation = 0.      ! angle (°) between axis X+ and North
  idecaly = 0        ! offset between canopy units along Y-axis
!      idecaly <> 0 : plantation en quinconce partiel (ie, decalage des Y
!      d'un nombre entier idecaly de cellules Y d'une maille a l'autre).
!             si idecaly = njy / 2 : quinconce parfait
!             si idecaly = 0       : plantation orthogonale
!      Cf. Subroutine Beampath

  nent=1     ! nent: number of vegetation types in the 3D grid
  nemax=1     ! nemax: maximum number of vegetation types in a voxel

  nvegmax=njx*njy*njz

  xrang=real(njx)*dx
  yrang=real(njy)*dy
  total_ground_area=xrang*yrang

! Allocation of allocatable arrays:
! In a first approximation, most arrays are over-allocated to NENT and NVEGMAX

  allocate(kxyz(njx,njy,njz+1))
  allocate(numx(nvegmax), numy(nvegmax), numz(nvegmax), nje(nvegmax))

  allocate(leafareadensity(nent,nvegmax), N_detailed(nent,nvegmax))
  allocate(nume(nent,nvegmax))

  allocate(S_vt_vx(nent,nvegmax)) ! Leaf area (m²) per voxel and vegetation type
  allocate(S_vx(nvegmax))        ! Leaf area (m²) per voxel
  allocate(S_vt(nent))      ! Leaf area (m²) per vegetation type
  allocate(volume_canopy(nent+1))
  allocate(voxel_canopy(nent))


  kxyz=0
  numx=0
  numy=0
  numz=0
  nje=1
  nume=1
  leafareadensity=0.
  N_detailed=2.

  nsol=njx*njy   ! Numbering soil surface areas
      do jx=1,njx
      do jy=1,njy
         kxyz(jx,jy,njz+1)=njy*(jx-1)+jy
  end do
  end do

  nblosoil=2     ! Number of wavebands for the soil surface
  allocate(rs(nblosoil))
  rs=0.       ! Soil reflectance in each band

   end subroutine g3d_create

!*******************************

   subroutine g3d_fill(fname,lecturestructure,pathResult)

  integer :: lecturestructure ! option for input file format of canopy structure data

  character*28 :: fname
  character*16 :: pathResult
  logical :: leafOK


  !write(*,*) 'Filling the 3D grid ...'
  !write(*,*)

!  Total canopy height: ztot
  do jz=1,njz
   ztot=ztot+dz(jz)
  end do

  volume_canopy=0.
  S_canopy=0.
  S_vx=0.
  S_vt=0.
  S_vt_vx=0.

  N_canopy=0.

  nemax=1     ! Maximum number of vegetation types in a voxel

!  File 2: Canopy structure
    select case (lecturestructure)

  Case (1)
!  Lecture d'un fichier de position de feuilles (type Pecher du Portugal)
  !fname='digital.'//spec
  open (2,file=fname)
  read(2,*) ! skip header line in file digital.<spec>

  N_canopy=0.
  nft=0
  k=0
  do while (.true.)
   read(2,*,end=998) jent, xx, yy, zz, s, azot

      xx=  xx/100.-xorig  ! Conversion from cm to m
      yy=  yy/100.-yorig  ! & translation according to grid origin
    zz= -(zz/100.-zorig)  ! Rem: Généralement les données de digitalisation ont un Z négatif


   leafOK=.TRUE.
   if (jent.gt.nent) then
    !write(*,*) 'Leaf #',nft+1,' belongs to vegetation type #',jent
    !write(*,*) 'while the 3Dgrid can contain only ',nent,' vegetation types.'
    !write(*,*) 'Please stop the program and redefine the 3Dgrid parameters.'
    !write(*,*) 'If not, leaf #',nft+1,'will be disregarded.'
    leafOK=.FALSE.
    !pause
   end if

   if (zz.le.0) then
    !write(*,*) 'Leaf #', nft,' is lower than 3D grid bottom'
    !write(*,*) 'Note that z-coordinates in the file should be negative, according to digitising data.'
    !write(*,*) 'Please stop the program and translate/correct leaf z-co-ordinates.'
    !write(*,*) 'If not, leaf #',nft+1,'will be disregarded.'
    leafOK=.FALSE.
    !pause
   endif

   if (s.le.0.01) then  ! leaf area lesser than 1 mm²
    !write(*,*) 'Area of leaf #', nft,' is lower than 1 mm²:',s*100.,' mm²'
    !write(*,*) 'Leaf #',nft+1,'will be disregarded.'
    leafOK=.FALSE.
    !pause
   endif

   if (leafOK) then
    nft=nft+1
    !write(*,*) 'Allocating leaf #', nft
    s=s/10000.    ! conversion from cm² to m²
    N_canopy=N_canopy+azot*s

    S_canopy = S_canopy + s
    S_vt(jent) = S_vt(jent) + s

 !   Affectation de la feuille a une cellule

    jx=nint(xx/dx)+1
    jx=modulo(jx-1,njx)+1
    jy=nint(yy/dy)+1
    jy=modulo(jy-1,njy)+1

     if (zz.gt.ztot) then
     !write(*,*) 'Leaf #', nft,' is higher than 3D grid height:',zz,' > ',ztot
     !write(*,*) 'Please stop the program and redefine the 3Dgrid parameters.'
     !write(*,*) 'If not, leaf #',nft+1,' will be included in the top layer.'
     !pause
     zz=ztot-dz(1)/2.
    endif
    jz=0
    zzz=ztot
    do while (zz.lt.zzz)
     jz=jz+1
     zzz=zzz-dz(jz)
    end do

  !    Cas ou il n'y avait encore rien dans la cellule (jx,jy,jz)
    if (kxyz(jx,jy,jz).eq.0) then
     k=k+1
     kxyz(jx,jy,jz)=k
     numx(k)=jx
     numy(k)=jy
     numz(k)=jz
     nje(k)=1
     nume(1,k)=jent
     leafareadensity(1,k)=s/(dx*dy*dz(jz))
     S_vt_vx(1,k)=s
     S_vx(k)=s
     N_detailed(1,k)=azot
    else
  !    Cas ou il y avait deja quelque chose dans la cellule (jx,jy,jz)
     kk=kxyz(jx,jy,jz)
     je=1
     do while ((nume(je,kk).ne.jent).and.(je.le.nje(kk)))
      je=je+1
     end do

       leafareadensity(je,kk)=leafareadensity(je,kk)+s/(dx*dy*dz(jz))
     N_detailed(je,kk)=(N_detailed(je,kk)*S_vt_vx(je,kk)+azot*s)/(S_vt_vx(je,kk)+s)
     S_vt_vx(je,kk) = S_vt_vx(je,kk) + s
     S_vx(kk) = S_vx(kk) + s
     nje(kk)=max(je,nje(kk))
     nemax=max(nemax,nje(kk))
     nume(je,kk)=jent
    endif
   end if
  end do   ! End of file
  998 continue
  close (2)

  !write(*,*)'Number of leaves in the canopy:',nft
  nveg=k

!  Writing a file : pathResult//leafarea.lfa

  fname= pathResult//"leafarea.lfa"
  open (2,file=fname)
  !write(2,*) '#voxel_x #voxel_y #voxel_z #vt LAD(m2 m3) N(g m-2) #voxel' !header

  do jent=1,nent
   do k=1,nveg
    do je=1,nje(k)
     if (jent.eq.nume(je,k)) then
      !write(2,22) numx(k),numy(k),numz(k),jent,leafareadensity(je,k),N_detailed(je,k), k
     endif
    end do
   end do
  end do

  close (2)
22  format(4(1x,i3),2(1x,f7.3),1x,i5)

!  Lecture d'un fichier type leafarea.<spec>: Leaf area density des cellules 3D
  Case (2)

  !fname='leafarea.'//spec
  open (2,file=fname)
  read(2,*) ! skip header line in file leafarea.<spec>

  k=0
  N_canopy=0.

  do while (.true.)
   read(2,*,end=999) jx,jy,jz,jent,ylad,azot
   if (jent.gt.nent) then
    !write(*,*) 'Voxel (',jx,',',jy,',',jz,') contains vegetation type #',jent
    !write(*,*) 'while the 3Dgrid can contain only ',nent,' vegetation types.'
    !write(*,*) 'Please stop the program and redefine the 3Dgrid parameters.'
    stop
   end if

!   ylad=ylad*factsf(jent)
   s=ylad*dx*dy*dz(jz)
   N_canopy=N_canopy+azot*s
   S_canopy = S_canopy + s
   S_vt(jent) = S_vt(jent) + s

   if (ylad.eq.0.) then
    !write(*,*) 'Voxel (jx=',jx,' jy=',jy,' jz=',jz,') does not contain vegetation type #',jent,'  !!'
   else
!   Cas ou il n'y avait encore rien dans la cellule (jx,jy,jz)
    if (kxyz(jx,jy,jz).eq.0) then
     k=k+1
     kxyz(jx,jy,jz)=k
     numx(k)=jx
     numy(k)=jy
     numz(k)=jz
     nje(k)=1
     nume(1,k)=jent
     leafareadensity(1,k)=ylad
     S_vt_vx(1,k)=ylad*dx*dy*dz(jz)
     S_vx(k)=ylad*dx*dy*dz(jz)
     N_detailed(1,k)=azot
    else
!      Cas ou il y avait deja quelque chose dans la cellule (jx,jy,jz)
!    Rem: Normalement, il n'y a pas encore composante jent dans la cellule
     kk=kxyz(jx,jy,jz)
     nje(kk)=nje(kk)+1
     nemax=max(nemax,nje(kk))
     nume(nje(kk),kk)=jent
     leafareadensity(nje(kk),kk)=ylad
     S_vt_vx(nje(kk),kk)=ylad*dx*dy*dz(jz)
     S_vx(kk)=ylad*dx*dy*dz(jz)
     N_detailed(nje(kk),kk)=azot
    endif
   endif

  end do
  999 continue
  close (2)
  nveg=k

  end select

  nsol=njx*njy   ! Numbering soil surface areas
      do jx=1,njx
      do jy=1,njy
         kxyz(jx,jy,njz+1)=njy*(jx-1)+jy
  end do
  end do

  N_canopy=N_canopy/S_canopy



  !write(*,*)'Number of vegetated cells:',nveg
  !write(*,*)'Number of soil surface areas:',nsol
  !write(*,*)'Total leaf area in the 3Dgrid (m-2):',S_canopy
  do k=1,nveg
   do je=1,nje(k)
    if (je.eq.1) then
     volume_canopy(nent+1)=volume_canopy(nent+1)+dx*dy*dz(numz(k))  ! Incrementing total canopy volume
    endif
    if (S_vt_vx(je,k).gt.0.) then
     volume_canopy(nume(je,k))=volume_canopy(nume(je,k))+dx*dy*dz(numz(k))
     voxel_canopy(nume(je,k))=voxel_canopy(nume(je,k))+1
    end if
   end do
  end do
  do jent=1,nent
   !write(*,*)'Volume occupied by vegetation type ',jent,' (m3) :', volume_canopy(jent),'   (',voxel_canopy(jent),')'
  end do
  !write(*,*)'Volume occupied by total canopy (m3) :', volume_canopy(nent+1)

  !write(*,*)'Average N nitrogen content (g m-2):',N_canopy
  !write(*,*)'Maximum number of vegetation types in one voxel:',nemax


   end subroutine g3d_fill

   subroutine g3d_destroy

  if (allocated(dz))      deallocate(dz)
  if (allocated(kxyz))      deallocate(kxyz)
  if (allocated(numx))      deallocate(numx)
  if (allocated(numy))      deallocate(numy)
  if (allocated(numz))      deallocate(numz)
  if (allocated(nje))      deallocate(nje)
  if (allocated(leafareadensity))  deallocate(leafareadensity)
  if (allocated(N_detailed))    deallocate(N_detailed)
  if (allocated(nume))      deallocate(nume)

  if (allocated(S_vt_vx))     deallocate(S_vt_vx)
  if (allocated(S_vx))      deallocate(S_vx)
  if (allocated(S_vt))      deallocate(S_vt)
  if (allocated(volume_canopy))   deallocate(volume_canopy)


  if (allocated(rs))      deallocate(rs)

   end subroutine g3d_destroy

end module grid3D

!------------------------------------------------------------------------------
