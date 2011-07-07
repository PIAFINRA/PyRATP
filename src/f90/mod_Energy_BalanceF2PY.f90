!------------------------------------------------------------------------------

module energy_balance

real, allocatable :: E_vt_vx(:,:)  ! Evaporation rate per voxel and vegetation type
real, allocatable :: E_vx(:)       ! Evaporation rate per voxel
real, allocatable :: E_vt(:)    ! Evaporation rate per vegetation type
real, allocatable :: E_ss_vt(:,:) ! Evaporation rate of shaded/sunlit area per vegetation type
real ::      E_ss(0:1)      ! Evaporation rate of canopy shaded/sunlit area
real ::      E_canopy         ! Evaporation rate of canopy
real ::      H_canopy         ! Sensible heat rate of canopy

real, allocatable :: ts(:,:,:)   ! Surface temperature of shaded/sunlit foliage of each vegetation type in each voxel
real, allocatable :: Sts(:,:)    ! Leaf area distribution per leaf temperature classes, for each vegetation type
real, allocatable :: gs(:,:,:)   ! Stomatal conductance (two sides) (m s-1) of shaded/sunlit are of each vegetation type in each voxel

real, allocatable :: rco2(:,:,:)  ! Total leaf resistance (2 sides, boundary layer + stomatal, s m-1) of each voxel for CO2 transport


contains

 subroutine eb_doall_mine

! Computation of the energy balance of each vegetation type in each voxel.
!   - compute net radiation, transpiration
!   - computestomatal conductance, leaf resistances
!   - compute leaf temperature
!   - take into account possible mined leaves (Cf. S. Pincebourde's thesis)

  use constant_values
  use grid3D
  use skyvault
  use vegetation_types
  use dir_interception
  use hemi_interception
  use micrometeo
  use shortwave_balance

real, allocatable :: E(:,:,:)   ! Latent heat flux by shaded/sunlit foliage of each vegetation type in each voxel

real, allocatable  :: raco2(:)   ! Leaf boundary layer resistance (s m-1) of each voxel for CO2 transport

real, allocatable  :: omega_factor(:,:,:) ! Decoupling factor of shaded/sunlit are of each vegetation type in each voxel



  real, allocatable :: rni(:,:,:)   ! Constant part in net radiation of shaded/sunlit foliage of each vegetation type in each voxel
  real, allocatable :: rayirt(:,:,:)  ! Thermal infrared radiation emitted by shaded/sunlit foliage of each vegetation type in each voxel

  real :: rayirtsol, ratm

  logical :: next_iter      ! .TRUE. if an additional iteration is needed to solve the energy balance
  integer :: niter        ! Iteration #
  real  :: bilanmax       ! Maximum departure from energy balance observed during a given iteration

  real  :: ga, ra       ! leaf boundary layer conductance (m s-1) / resistance (s m-1)
  real  :: es, des       ! Saturating water vapor pressure (Pa), and its derivative with regard to leaf temperature

  real  :: rss, rsi, drsi     ! Stomatal resistance / conductance of upper (rss) and lower (rsi, gsi) sides, and some derivatives

  integer :: jent        ! Current vegetation type #
  real  :: leaf_nitrogen, par_irrad, leaf_temp, VPDair ! Input parameters for Jarvis stomatal model

  real  :: rv, drv, rh      ! Total resistance to water vapour (rv) and heat (rh) transfer, and derivative of rv
  real  :: rn, drn       ! Net radiation of current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative
  real  :: devap        ! Derivative of current latent heat flux (with regard to temperature)
  real  :: h, dh        ! Sensible heat flux from current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative
  real  :: hem, dhem      ! Heat exchange between mine and healthy tissue (W m-2), and its derivative
  real  :: bilan, dbilan     ! Departure from energy balance in current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative

  real  :: rssCO2, rsico2     ! Lower ans upper side stomatal resistance (s m-1) for CO2 transport

  real :: epsilon          ! Intermediate term in decoupling factor calcultation

  integer :: tsclass

  call cv_set ! Setting physical constant values ...


!  Allocation of module arrays

  call eb_destroy

  allocate(E_vt_vx(nemax,nveg))
  allocate(E_vx(nveg))
  allocate(E_vt(nent))
  allocate(E_ss_vt(0:1,nent))

  allocate(ts(0:1,nemax,nveg))
  allocate(gs(0:1,nemax,nveg))
  allocate(rco2(0:1,nemax,nveg))

  allocate(Sts(nent,0:100))

!  Initialisation of output variables for energy balance:

  E_vt_vx = 0.  ! Evaporation rate per voxel and vegetation type
  E_vx = 0.       ! Evaporation rate per voxel
  E_vt = 0.    ! Evaporation rate per vegetation type
  E_ss_vt = 0. ! Evaporation rate of shaded/sunlit area per vegetation type
  E_ss = 0.      ! Evaporation rate of canopy shaded/sunlit area
  E_canopy = 0.      ! Evaporation rate of canopy
  H_canopy = 0.      ! Sensible heat rate of canopy

  Sts=0.

!  Allocation of local arrays

  allocate(E(0:1,nemax,nveg))
  allocate(raco2(nveg))
  allocate(omega_factor(0:1,nemax,nveg))
  allocate(rni(0:1,nemax,nveg))
  allocate(rayirt(0:1,nemax,nveg))


!  Starting net radiation balance

  rayirtsol=sigma*(tsol+273.15)**4*dx*dy  ! TIR radiation emitted by each ground zone (W)
  do k=1,nveg
  do je=1,nje(k)
!   Contribution of atmospheric radiation to long wave radiation balance of type je in voxel k
         ratm=ratmos*rdiv(je,k)/S_vt_vx(je,k)
!   Contribution of TIR radiation emitted by ground zones ksol, ksol=1,nsol
   rsol=0.
   do ksol=1,nsol
    rsol=rsol+ffvs(k,je,ksol)
   end do
         rsol=rsol*rayirtsol/S_vt_vx(je,k)

         do joe=0,1
            rni(joe,je,k)=SWRA_detailed(joe,je,k)+ratm+rsol
   end do
  end do
  end do

!-----------------------------!
!  Starting energy balance !
!-----------------------------!

!
!  Initialisation of leaf temperature, i.e. equal to air temperature taref
!
  do k=1,nveg
  do je=1,nje(k)
  do joe=0,1
   ts(joe,je,k)=taref
         rayirt(joe,je,k)=2.*sigma*(taref+273.15)**4*S_detailed(joe,je,k)  ! TIR radiation flux emitted by shaded / sunlit vegetation in voxels (including 2 sides)
  end do
  end do
  end do

!
!  Iterative solving of energy balance for each vegetation type in each voxel
!

      niter=0
  next_iter=.TRUE.

  do while (next_iter)

   niter=niter+1
   !write(*,*) 'Iteration:',niter

   bilanmax=0.
   E_canopy=0. ! Pour essai Shuttleworth-Wallace (09 Dec 2002, avec FB)
   H_canopy=0.    ! idem

   do k=1,nveg     ! Computation of the energy balance

   do je=1,nje(k)    ! For each voxel, each vegetation type, shaded and sunlit area

   do joe=0,1
   !write(*,*) 'joe:',joe

    jent=nume(je,k)
    !write(*,*) 'jent:',jent
    leaf_nitrogen = N_detailed(je,k)
    par_irrad=PARirrad(joe,je,k)
    leaf_temp=ts(joe,je,k)
    esair=610.78*exp((17.27*taref)/(237.3+taref))
    VPDair=esair-earef
    !write(*,*) 'VPDair:',VPDair
!    Leaf boundary resistance / conductance
!
!    ra : one-side resistance, in s.m-1
!    ga : one-side conductance, in m s-1
    !write(*,*) 'numz(k)',numz(k)
    !write(*,*) 'uref(numz(k))',uref(numz(k))
    ga=Aga(jent,1)*uref(numz(k))+Aga(jent,2)

    !write(*,*) 'ga',ga
    ra=1./ga

!    Saturating water vapor pressure, es, at temperature ts: Tetens' formula (1930), en Pa
!    and its derivative des, with regard to temperature ts

    es=610.78*exp((17.27*ts(joe,je,k))/(237.3+ts(joe,je,k)))
    des=610.78*17.27*237.3/((237.3+ts(joe,je,k))**2)*exp((17.27*ts(joe,je,k))/(237.3+ts(joe,je,k)))


!    Stomatal resistance (in s m-1) / conductance (in m s-1)
!    rss:  upper side stomatal resistance
!    rsi:  lower side stomatal resistance
!    gs :  lower side stomatal conductance

    rss=10000.    ! Arbitrary high value
    !write(*,*) 'call Jarvis_stomata avant'
    call Jarvis_stomata(jent,leaf_nitrogen,par_irrad,caref,leaf_temp,VPDair,ga,rsi,drsi)
    !write(*,*) 'call Jarvis_stomata apres'

!    Total resistances, i.e. boundary layer + stomatal and 2 sides, in s m-1
!    rv : water vapour transfert
!    rh : heat transfert

    if (es.lt.earef) then   ! Saturation at leaf surface (i.e. dew formation)
     rv=ra/2.
     drv=0.
     else
     rv=(rss+ra)*(rsi+ra)/(rss+rsi+2.*ra)
     drv=((rss+ra)/(rss+rsi+2*ra))**2*drsi
    endif

    rh=ra/2.

!
!    Computation of the energy terms of the energy balance
!    (as a function of leaf temperature)

!    1- Net radiation : rn (W m-2)

    rn=rni(joe,je,k)
    do ks=1,nveg    ! Contribution of emitted radiation by shaded / sunlit vegetation in every voxel
    do jes=1,nje(ks)
    do joes=0,1
     rn=rn+ffvv(k,je,ks,jes)*rayirt(joes,jes,ks)/S_vt_vx(je,k)
    end do
    end do
    end do
    rn=rn-rayirt(joe,je,k)/S_detailed(joe,je,k)

!    1'- Derivative of net radiation with regard to leaf temperature: drn

    drn=2*4*sigma*(ts(joe,je,k)+273.15)**3*(ffvv(k,je,k,je)*S_detailed(joe,je,k)/(S_vt_vx(je,k))-1.)


!    2- Latent heat flux: evap, in W m-2

    E(joe,je,k)=(rho*cp/gamma)*(es-earef)/rv
    E_canopy=E_canopy+E(joe,je,k)*S_detailed(joe,je,k)

!    2'- Derivative of latent heat flux with regard to leaf temperature: devap

    devap=(rho*cp/gamma)*(des*rv-(es-earef)*drv)/rv**2


!    3- Sensible heat flux: h (W m-2)

    h=(rho*cp)*(ts(joe,je,k)-taref)/rh
    H_canopy=H_canopy+h*S_detailed(joe,je,k)

!    3'- Derivative of sensible heat flux with regard to leaf temperature: dh

    dh=rho*cp/rh

!    4-  Heat exchange between the mine and healthy tissue : Cf. Thèse S. Pincebourde

    hem= float(ismine(jent))*(rho*cp)*(ts(joe,je,k)-ts(joe,1,k))*&
     &(0.05*(22.4/1000.)*(abs(ts(joe,je,k)-ts(joe,1,k))/epm(jent))**0.25)*0.13

!    rem: This assumes that healthy tissue is vegetation type #1.

!    4'- Derivative of heat exchange between the mine and healthy tissue

!    dhem= float(ismine(jent))*(rho*cp)*(0.05*(1000./22.4)/(epm(jent))**(0.25))*1.25*abs(ts(joe,je,k)-ts(joe,1,k))**0.25*0.13
    if (abs(hem).lt.1.e-5) then
     dhem=0.
    else
     dhem=float(ismine(jent))*(rho*cp)*(0.05*(22.4/1000.)/&
     &(epm(jent))**(0.25))*(abs(ts(joe,je,k)-ts(joe,1,k))&
     &**0.25+0.25*(ts(joe,je,k)-ts(joe,1,k))/abs(ts(joe,je,k)&
     &-ts(joe,1,k))**0.75)*0.13
    endif

!    5- Energy balance (bilan) and its derivative (dbilan)

    bilan=rn-E(joe,je,k)-h-hem
    dbilan=drn-devap-dh-dhem
    bilanmax=amax1(bilanmax,abs(bilan))

!    6- Updating leaf temperature (and emitted TIR radiation) for next iteration

    ts(joe,je,k)=ts(joe,je,k)-(bilan/dbilan)
    rayirt(joe,je,k)=2.*sigma*(ts(joe,je,k)+273.15)**4*S_detailed(joe,je,k)


!    Computation of resistances to CO2 transport (in s m-1)
!
    raco2(k)=1.37*ra    ! Leaf boundary layer resistance for CO2 transfert
    rssco2=1.6*rss     ! Upper side stomatal resistance for CO2 transfert
    rsico2=1.6*rsi     ! Lower side stomatal resistance for CO2 transfert
!    Total resistance to CO2 transfert, i.e. leaf boundary layer + stomatal and 2 sides
    rco2(joe,je,k)=(rssco2+raco2(k))*(rsico2+raco2(k))/(rssco2+rsico2+2.*raco2(k))
!    Conversion to µmol CO2-1 m2 s   (a 25 °C)
    rco2(joe,je,k)=rco2(joe,je,k)/1000./0.0414 / 1.e6


!    Computation of the decoupling factor (omega), Jarvis et Mc Naughton (1986)
!
    gs(joe,je,k)=1/rss + 1/rsi
    epsilon=des/gamma + 2.
    omega_factor(joe,je,k)=epsilon/(epsilon + 2. * ga/gs(joe,je,k) )

   end do    ! Loop-end of computation of the energy balance
   end do
   end do

   !write(*,*) 'Iteration #',niter,'Maximum deviation from energy balance (W m-2): ',bilanmax

   next_iter = (bilanmax.gt.1).and.(niter.lt.100)

  end do

!  Summing up evaporation rates at different levels

  do k=1,nveg
   do je=1,nje(k)
    jent=nume(je,k)
    do joe=0,1
     E(joe,je,k) = E(joe,je,k) * S_detailed(joe,je,k)/lambda/18*1000.  ! Evaporation rate in mmol H20 s-1
     E_vt_vx(je,k) = E_vt_vx(je,k) + E(joe,je,k)
     E_vx(k) = E_vx(k) + E(joe,je,k)
     E_vt(jent) = E_vt(jent) + E(joe,je,k)
     E_ss_vt(joe,jent) = E_ss_vt(joe,jent) + E(joe,je,k)
     E_ss(joe) = E_ss(joe) + E(joe,je,k)
    end do
   end do
  end do
  E_canopy = E_canopy / lambda/18*1000.  ! Evaporation rate in mmol H20 s-1


!  Normalisation of Es by leaf area

  do k=1,nveg
   do je=1,nje(k)
    E_vt_vx(je,k)=E_vt_vx(je,k)/S_vt_vx(je,k)
   end do
   E_vx(k)=E_vx(k)/S_vx(k)
  end do
  do jent=1,nent
   do joe=0,1
    E_ss_vt(joe,jent)=E_ss_vt(joe,jent)/S_ss_vt(joe,jent)
   end do
   E_vt(jent)=E_vt(jent)/S_vt(jent)
  end do
  do joe=0,1
   E_ss(joe)=E_ss(joe)/S_ss(joe)
  end do
  E_canopy = E_canopy / S_canopy
  H_canopy = H_canopy / S_canopy


!  Distribution of leaf temperature at canopy scale

  do k=1,nveg
   do je=1,nje(k)
    do joe=0,1
     tsclass=int(ts(joe,je,k))+1
     Sts(nume(je,k),tsclass)=Sts(nume(je,k),tsclass)+S_detailed(joe,je,k)
    end do
   end do
  end do



!  write(*,*) 'gs',gs(0,1,kxyz(4,9,8)),gs(1,1,kxyz(4,9,8))
!  write(*,*) 'rni',rni(0,1,kxyz(4,9,8)),rni(1,1,kxyz(4,9,8))


! Deallocation of local arrays used in subroutine eb_doall
  deallocate(E)     ! Latent heat flux by shaded/sunlit foliage of each vegetation type in each voxel
  deallocate(raco2)    ! Leaf boundary layer resistance (s m-1) of each voxel for CO2 transport
!  deallocate(gs)     ! Stomatal conductance (two sides) (m s-1) of shaded/sunlit are of each vegetation type in each voxel
  deallocate(omega_factor) ! Decoupling factor of shaded/sunlit are of each vegetation type in each voxel
  deallocate(rni)    ! Constant part in net radiation of shaded/sunlit foliage of each vegetation type in each voxel
  deallocate(rayirt)   ! Thermal infrared radiation emitted by shaded/sunlit foliage of each vegetation type in each voxel

 end subroutine eb_doall_mine
!-----------------------------------------------------------eb_doall-------------------------------------------------------------
 subroutine eb_doall

! Computation of the energy balance of each vegetation type in each voxel.
!   - compute net radiation, transpiration
!   - computestomatal conductance, leaf resistances
!   - compute leaf temperature


  use constant_values
  use grid3D
  use skyvault
  use vegetation_types
  use dir_interception
  use hemi_interception
  use micrometeo
  use shortwave_balance

real, allocatable :: E(:,:,:)   ! Latent heat flux by shaded/sunlit foliage of each vegetation type in each voxel

real, allocatable  :: raco2(:)   ! Leaf boundary layer resistance (s m-1) of each voxel for CO2 transport

real, allocatable  :: omega_factor(:,:,:) ! Decoupling factor of shaded/sunlit are of each vegetation type in each voxel



  real, allocatable :: rni(:,:,:)   ! Constant part in net radiation of shaded/sunlit foliage of each vegetation type in each voxel
  real, allocatable :: rayirt(:,:,:)  ! Thermal infrared radiation emitted by shaded/sunlit foliage of each vegetation type in each voxel

  real :: rayirtsol, ratm

  logical :: next_iter      ! .TRUE. if an additional iteration is needed to solve the energy balance
  integer :: niter        ! Iteration #
  real  :: bilanmax       ! Maximum departure from energy balance observed during a given iteration

  real  :: ga, ra       ! leaf boundary layer conductance (m s-1) / resistance (s m-1)
  real  :: es, des       ! Saturating water vapor pressure (Pa), and its derivative with regard to leaf temperature

  real  :: rss, rsi, drsi     ! Stomatal resistance / conductance of upper (rss) and lower (rsi, gsi) sides, and some derivatives

  integer :: jent        ! Current vegetation type #
  real  :: leaf_nitrogen, par_irrad, leaf_temp, VPDair ! Input parameters for Jarvis stomatal model

  real  :: rv, drv, rh      ! Total resistance to water vapour (rv) and heat (rh) transfer, and derivative of rv
  real  :: rn, drn       ! Net radiation of current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative
  real  :: devap        ! Derivative of current latent heat flux (with regard to temperature)
  real  :: h, dh        ! Sensible heat flux from current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative
  real  :: bilan, dbilan     ! Departure from energy balance in current shaded / sunlit vegetation type in currentvoxel (W m-2), and its derivative

  real  :: rssCO2, rsico2     ! Lower ans upper side stomatal resistance (s m-1) for CO2 transport

  real :: epsilon          ! Intermediate term in decoupling factor calcultation

  integer :: tsclass

  call cv_set ! Setting physical constant values ...


!  Allocation of module arrays

  call eb_destroy

  allocate(E_vt_vx(nemax,nveg))
  allocate(E_vx(nveg))
  allocate(E_vt(nent))
  allocate(E_ss_vt(0:1,nent))

  allocate(ts(0:1,nemax,nveg))
  allocate(gs(0:1,nemax,nveg))
  allocate(rco2(0:1,nemax,nveg))

  allocate(Sts(nent,0:100))

!  Initialisation of output variables for energy balance:

  E_vt_vx = 0.  ! Evaporation rate per voxel and vegetation type
  E_vx = 0.       ! Evaporation rate per voxel
  E_vt = 0.    ! Evaporation rate per vegetation type
  E_ss_vt = 0. ! Evaporation rate of shaded/sunlit area per vegetation type
  E_ss = 0.      ! Evaporation rate of canopy shaded/sunlit area
  E_canopy = 0.      ! Evaporation rate of canopy
  H_canopy = 0.      ! Sensible heat rate of canopy

  Sts=0.

!  Allocation of local arrays

  allocate(E(0:1,nemax,nveg))
  allocate(raco2(nveg))
  allocate(omega_factor(0:1,nemax,nveg))
  allocate(rni(0:1,nemax,nveg))
  allocate(rayirt(0:1,nemax,nveg))


!  Starting net radiation balance

  rayirtsol=sigma*(tsol+273.15)**4*dx*dy  ! TIR radiation emitted by each ground zone (W)
  do k=1,nveg
  do je=1,nje(k)
!   Contribution of atmospheric radiation to long wave radiation balance of type je in voxel k
         ratm=ratmos*rdiv(je,k)/S_vt_vx(je,k)
!   Contribution of TIR radiation emitted by ground zones ksol, ksol=1,nsol
   rsol=0.
   do ksol=1,nsol
    rsol=rsol+ffvs(k,je,ksol)
   end do
         rsol=rsol*rayirtsol/S_vt_vx(je,k)

         do joe=0,1
            rni(joe,je,k)=SWRA_detailed(joe,je,k)+ratm+rsol
   end do
  end do
  end do

!-----------------------------!
!  Starting energy balance !
!-----------------------------!

!
!  Initialisation of leaf temperature, i.e. equal to air temperature taref
!
  do k=1,nveg
  do je=1,nje(k)
  do joe=0,1
   ts(joe,je,k)=taref
         rayirt(joe,je,k)=2.*sigma*(taref+273.15)**4*S_detailed(joe,je,k)  ! TIR radiation flux emitted by shaded / sunlit vegetation in voxels (including 2 sides)
  end do
  end do
  end do

!
!  Iterative solving of energy balance for each vegetation type in each voxel
!

      niter=0
  next_iter=.TRUE.

  do while (next_iter)

   niter=niter+1
   !write(*,*) 'Iteration:',niter

   bilanmax=0.
   E_canopy=0. ! Pour essai Shuttleworth-Wallace (09 Dec 2002, avec FB)
   H_canopy=0.    ! idem

   do k=1,nveg     ! Computation of the energy balance

   do je=1,nje(k)    ! For each voxel, each vegetation type, shaded and sunlit area

   do joe=0,1
   !write(*,*) 'joe:',joe

    jent=nume(je,k)
    !write(*,*) 'jent:',jent
    leaf_nitrogen = N_detailed(je,k)
    par_irrad=PARirrad(joe,je,k)
    leaf_temp=ts(joe,je,k)
    esair=610.78*exp((17.27*taref)/(237.3+taref))
    VPDair=esair-earef
    !write(*,*) 'VPDair:',VPDair
!    Leaf boundary resistance / conductance
!
!    ra : one-side resistance, in s.m-1
!    ga : one-side conductance, in m s-1
    !write(*,*) 'numz(k)',numz(k)
    !write(*,*) 'uref(numz(k))',uref(numz(k))
    ga=Aga(jent,1)*uref(numz(k))+Aga(jent,2)

    !write(*,*) 'ga',ga
    ra=1./ga

!    Saturating water vapor pressure, es, at temperature ts: Tetens' formula (1930), en Pa
!    and its derivative des, with regard to temperature ts

    es=610.78*exp((17.27*ts(joe,je,k))/(237.3+ts(joe,je,k)))
    des=610.78*17.27*237.3/((237.3+ts(joe,je,k))**2)*exp((17.27*ts(joe,je,k))/(237.3+ts(joe,je,k)))


!    Stomatal resistance (in s m-1) / conductance (in m s-1)
!    rss:  upper side stomatal resistance
!    rsi:  lower side stomatal resistance
!    gs :  lower side stomatal conductance

    rss=10000.    ! Arbitrary high value
    !write(*,*) 'call Jarvis_stomata avant'
    call Jarvis_stomata(jent,leaf_nitrogen,par_irrad,caref,leaf_temp,VPDair,ga,rsi,drsi)
    !write(*,*) 'call Jarvis_stomata apres'

!    Total resistances, i.e. boundary layer + stomatal and 2 sides, in s m-1
!    rv : water vapour transfert
!    rh : heat transfert

    if (es.lt.earef) then   ! Saturation at leaf surface (i.e. dew formation)
     rv=ra/2.
     drv=0.
     else
     rv=(rss+ra)*(rsi+ra)/(rss+rsi+2.*ra)
     drv=((rss+ra)/(rss+rsi+2*ra))**2*drsi
    endif

    rh=ra/2.

!
!    Computation of the energy terms of the energy balance
!    (as a function of leaf temperature)

!    1- Net radiation : rn (W m-2)

    rn=rni(joe,je,k)
    do ks=1,nveg    ! Contribution of emitted radiation by shaded / sunlit vegetation in every voxel
    do jes=1,nje(ks)
    do joes=0,1
     rn=rn+ffvv(k,je,ks,jes)*rayirt(joes,jes,ks)/S_vt_vx(je,k)
    end do
    end do
    end do
    rn=rn-rayirt(joe,je,k)/S_detailed(joe,je,k)

!    1'- Derivative of net radiation with regard to leaf temperature: drn

    drn=2*4*sigma*(ts(joe,je,k)+273.15)**3*(ffvv(k,je,k,je)*S_detailed(joe,je,k)/(S_vt_vx(je,k))-1.)


!    2- Latent heat flux: evap, in W m-2

    E(joe,je,k)=(rho*cp/gamma)*(es-earef)/rv
    E_canopy=E_canopy+E(joe,je,k)*S_detailed(joe,je,k)

!    2'- Derivative of latent heat flux with regard to leaf temperature: devap

    devap=(rho*cp/gamma)*(des*rv-(es-earef)*drv)/rv**2


!    3- Sensible heat flux: h (W m-2)

    h=(rho*cp)*(ts(joe,je,k)-taref)/rh
    H_canopy=H_canopy+h*S_detailed(joe,je,k)

!    3'- Derivative of sensible heat flux with regard to leaf temperature: dh

    dh=rho*cp/rh

!    5- Energy balance (bilan) and its derivative (dbilan)

    bilan=rn-E(joe,je,k)-h
    dbilan=drn-devap-dh
    bilanmax=amax1(bilanmax,abs(bilan))

!    6- Updating leaf temperature (and emitted TIR radiation) for next iteration

    ts(joe,je,k)=ts(joe,je,k)-(bilan/dbilan)
    rayirt(joe,je,k)=2.*sigma*(ts(joe,je,k)+273.15)**4*S_detailed(joe,je,k)


!    Computation of resistances to CO2 transport (in s m-1)
!
    raco2(k)=1.37*ra    ! Leaf boundary layer resistance for CO2 transfert
    rssco2=1.6*rss     ! Upper side stomatal resistance for CO2 transfert
    rsico2=1.6*rsi     ! Lower side stomatal resistance for CO2 transfert
!    Total resistance to CO2 transfert, i.e. leaf boundary layer + stomatal and 2 sides
    rco2(joe,je,k)=(rssco2+raco2(k))*(rsico2+raco2(k))/(rssco2+rsico2+2.*raco2(k))
!    Conversion to µmol CO2-1 m2 s   (a 25 °C)
    rco2(joe,je,k)=rco2(joe,je,k)/1000./0.0414 / 1.e6


!    Computation of the decoupling factor (omega), Jarvis et Mc Naughton (1986)
!
    gs(joe,je,k)=1/rss + 1/rsi
    epsilon=des/gamma + 2.
    omega_factor(joe,je,k)=epsilon/(epsilon + 2. * ga/gs(joe,je,k) )

   end do    ! Loop-end of computation of the energy balance
   end do
   end do

   !write(*,*) 'Iteration #',niter,'Maximum deviation from energy balance (W m-2): ',bilanmax

   next_iter = (bilanmax.gt.1).and.(niter.lt.100)

  end do

!  Summing up evaporation rates at different levels

  do k=1,nveg
   do je=1,nje(k)
    jent=nume(je,k)
    do joe=0,1
     E(joe,je,k) = E(joe,je,k) * S_detailed(joe,je,k)/lambda/18*1000.  ! Evaporation rate in mmol H20 s-1
     E_vt_vx(je,k) = E_vt_vx(je,k) + E(joe,je,k)
     E_vx(k) = E_vx(k) + E(joe,je,k)
     E_vt(jent) = E_vt(jent) + E(joe,je,k)
     E_ss_vt(joe,jent) = E_ss_vt(joe,jent) + E(joe,je,k)
     E_ss(joe) = E_ss(joe) + E(joe,je,k)
    end do
   end do
  end do
  E_canopy = E_canopy / lambda/18*1000.  ! Evaporation rate in mmol H20 s-1


!  Normalisation of Es by leaf area

  do k=1,nveg
   do je=1,nje(k)
    E_vt_vx(je,k)=E_vt_vx(je,k)/S_vt_vx(je,k)
   end do
   E_vx(k)=E_vx(k)/S_vx(k)
  end do
  do jent=1,nent
   do joe=0,1
    E_ss_vt(joe,jent)=E_ss_vt(joe,jent)/S_ss_vt(joe,jent)
   end do
   E_vt(jent)=E_vt(jent)/S_vt(jent)
  end do
  do joe=0,1
   E_ss(joe)=E_ss(joe)/S_ss(joe)
  end do
  E_canopy = E_canopy / S_canopy
  H_canopy = H_canopy / S_canopy


!  Distribution of leaf temperature at canopy scale

  do k=1,nveg
   do je=1,nje(k)
    do joe=0,1
     tsclass=int(ts(joe,je,k))+1
     Sts(nume(je,k),tsclass)=Sts(nume(je,k),tsclass)+S_detailed(joe,je,k)
    end do
   end do
  end do



!  write(*,*) 'gs',gs(0,1,kxyz(4,9,8)),gs(1,1,kxyz(4,9,8))
!  write(*,*) 'rni',rni(0,1,kxyz(4,9,8)),rni(1,1,kxyz(4,9,8))


! Deallocation of local arrays used in subroutine eb_doall
  deallocate(E)     ! Latent heat flux by shaded/sunlit foliage of each vegetation type in each voxel
  deallocate(raco2)    ! Leaf boundary layer resistance (s m-1) of each voxel for CO2 transport
!  deallocate(gs)     ! Stomatal conductance (two sides) (m s-1) of shaded/sunlit are of each vegetation type in each voxel
  deallocate(omega_factor) ! Decoupling factor of shaded/sunlit are of each vegetation type in each voxel
  deallocate(rni)    ! Constant part in net radiation of shaded/sunlit foliage of each vegetation type in each voxel
  deallocate(rayirt)   ! Thermal infrared radiation emitted by shaded/sunlit foliage of each vegetation type in each voxel

 end subroutine eb_doall
!------------------------------------------------------------------end  eb_doall

 subroutine Jarvis_stomata(jent,leaf_nitrogen,par_irrad,ca,leaf_temp, VPDair,ga,rsi,drsi)

 use vegetation_types

!  Jarvis model (1976), modified by Le Roux et al. (1999) for inclusion of Na effect
!  Stomatal conductance: gs, in m s-1

!  Input variables
  integer :: jent  ! Vegetation type #, needed to get the suitable gs response parameters.
  real  :: leaf_nitrogen ! leaf nitrogen content Na (g m-2)
  real  :: par_irrad, ca, leaf_temp, VPDair, ga ! microclimate variables sensed by the leaf, plus leaf boundary conductance as needed in solving coupling between gs and VPD

  real  :: VPDthreshold ! VPD value below which fgsVPD = cte = fgsVPD(VPDthreshold)

!  Output variables: stomatal conductance (m s-1) / resistance (s m-1), and derivatives with regard to leaf temperature
  real  :: gsi, rsi, dgsi, drsi

  real  :: gsmax    ! Maximum gs (m s-1), as a function of leaf nitrogen content Na (g m-2)
  real  :: fgsPAR   ! Reducing factor of PAR irradiance on gs
  real  :: fgsCA    ! Reducing factor of air CO2 partial pressure on gs
  real  :: fgsLT    ! Reducing factor of leaf temperature on gs
  real  :: fgsVPD0   ! Reducing factor of VPD on gs, for leaf VPD = 0
  real  :: fgsVPDair  ! Reducing factor of VPD on gs, for leaf VPD = air VPD
  real  :: fgsVPDt   ! Reducing factor of VPD on gs, for leaf VPD = VPDthreshold
  real  :: gsVPD0   ! Stomatal conductance at leaf VPD = 0
  real  :: gsVPDair   ! Stomatal conductance at leaf VPD = air VPD

  real  :: dfgsLT   ! Derivative of fgsLT with regard to leaf temperature
  real  :: dgsVP0   ! Derivative of gsVP0 with regard to leaf temperature
  real  :: dgsVPair   ! Derivative of gsVPair with regard to leaf temperature
  real  :: des    ! Derivative of saturating water vapour pressure with regard to leaf temperature

!  Step #1: maximum gs, as a function of leaf nitrogen content Na (g m-2)
!  AgsN = 2.002 * 1.e-3  !Paramètres pour Noyer
!  BgsN = 0.740 * 1.e-3
      gsmax=AgsN(jent,1)*leaf_nitrogen+AgsN(jent,2)

!  Step #2: effect of PAR irradiance on gs, i.e. reducing factor : fgsPAR
  select case (i_gsPAR(jent)) ! type of equation for gs response to PAR

   case (1)  ! gs=f(PAR) : 2nd order polynomial function

!   AgsPAR = -3.752 * 1.e-7  ! Paramètres Noyer (ajustement données jeune Noyer a CO2 ambiant (Juillet 2000)
!   BgsPAR = 1.105 * 1.e-3
!   CgsPAR = 0.183

   if (par_irrad.gt.1500.) then
    fgsPAR=1.00
   else
    fgsPAR=AgsPAR(jent,1)*par_irrad**2+AgsPAR(jent,2)*par_irrad+AgsPAR(jent,3)
   endif

   case (2) ! gs=f(PAR) : hyperbola (a PAR + b) / (c PAR +d) : i.e. 4 parameters

   fgsPAR=(AgsPAR(jent,1)*par_irrad+AgsPAR(jent,2))/(AgsPAR(jent,3)*par_irrad+AgsPAR(jent,4))

   case (3) ! gs=f(PAR) : function (a PAR² + b PAR + c) / (d PAR² + e PAR + f) : i.e. 6 parameters

   fgsPAR=(AgsPAR(jent,1)*par_irrad**2+AgsPAR(jent,2)*&
   &par_irrad+AgsPAR(jent,3))/(AgsPAR(jent,4)*par_irrad**2+&
   &AgsPAR(jent,5)*par_irrad+AgsPAR(jent,6))

   case (4) ! gs=f(PAR) : function (a sqrt(PAR) + b) / (c PAR + d sqrt(PAR) + e) : i.e. 5 parameters

   fgsPAR=(AgsPAR(jent,1)*sqrt(par_irrad)+AgsPAR(jent,2))/(AgsPAR(jent,3)*&
   &par_irrad+AgsPAR(jent,4)*sqrt(par_irrad)+AgsPAR(jent,5))

   case (5) ! gs=f(PAR) : function a / (b + [(PAR-c)/d]²) : i.e. 4 parameters

   fgsPAR= AgsPAR(jent,1)/(AgsPAR(jent,2)+&
   &((par_irrad-AgsPAR(jent,3))/AgsPAR(jent,4))**2)

   case default

   fgsPAR=1.00

  end select

!  Step #3: effect of partial CO2 pressure on gs, i.e. reducing factor fgsCA
  select case (i_gsCA(jent))    ! type of equation for gs response to CO2 partial pressure

   case (1) ! gs=f(ca) : 2nd order polynomial function

!   AgsCA = 2.32e-4    ! Paramètres Noyer de Plauzat
!   BgsCA = -4.02e-2
!   CgsCA = 2.07

   fgsCA=AgsCA(jent,1) * ca**2 + AgsCA(jent,2) * ca + AgsCA(jent,3)

   case default

   fgsCA=1.00

  end select

!  Step #4: effect of leaf temperature on gs, i.e. reducing factor fgsLT
  select case (i_gsLT(jent))    ! type of equation for gs response to leaf temperature

   case (1) ! gs=f(leaf_temp) : 2nd order polynomial function

!   AgsLT = -4.82e-3   ! Paramètres Noyer de Plauzat
!   BgsLT = 0.24165
!   CgsLT = -2.029

   fgsLT=amax1(AgsLT(jent,1)*leaf_temp**2+AgsLT(jent,2)*leaf_temp+AgsLT(jent,3),0.05)

   case (3) ! gs=f(leaf_temp) : function (a LT² + b LT + c) / (d LT² + e LT + f) : i.e. 6 parameters

   fgsLT=(AgsLT(jent,1)*leaf_temp**2+AgsLT(jent,2)*leaf_temp+AgsLT(jent,3))/&
   &(AgsLT(jent,4)*leaf_temp**2+AgsLT(jent,5)*leaf_temp+AgsLT(jent,6))

   case (4) ! gs=f(leaf_temp) : function (a sqrt(LT) + b) / (c LT + d sqrt(LT) + e) : i.e. 5 parameters

   fgsLT=(AgsLT(jent,1)*sqrt(leaf_temp)+AgsLT(jent,2))/&
   &(AgsLT(jent,3)*leaf_temp+AgsLT(jent,4)*sqrt(leaf_temp)+AgsLT(jent,5))

   case (5) ! gs=f(leaf_temp) : function a / (b + [(LT-c)/d]²) : i.e. 4 parameters

   fgsLT=AgsLT(jent,1)/(AgsLT(jent,2)+&
   &((leaf_temp-AgsLT(jent,3))/AgsLT(jent,4))**2)

   case default

   fgsLT=1.00

  end select

!  Step #5: effect of air VPD on gs: a little bit more complicated !
!      because gs does not respond to air VPD, but to leaf surface VPD
!      Coupling between VPD and gs must thus be solved.
!      Gs response to VPD is assumed to be linear: fgsVPD = AgsVPD* VPDleaf + BgsVPD
!      Improved solving as reported in SAFE booklet (H. Sinoquet, 23 dec 2002)
!      gs = (1/2) [ square_root{ [ga - gs(VPDleaf=0)]² + 4 ga gs(VPDleaf=VPDair) } - [ga - gs(VPDleaf=0)]  ]
!    Two major advantages:
!  1- Intermediate variables have some biological meaning
!  2- Analytical derivation of gs with regard to leaf temperature is possible

!  AgsVPD = -1.8e-4  ! Paramètres Noyer de Plauzat
!  BgsVPD = 1.18

!  Addendum 09 June 2004: Threshold value for VPD, i.e. below threshold value fgsVPD= cte = fgsVPD(VPDthreshold)
!          For Noyer de Plauzat: VPDthreshold = 1000 Pa

  VPDthreshold=AgsVPD(jent,3)
  fgsVPDt = AgsVPD(jent,1) * VPDthreshold + AgsVPD(jent,2)

  fgsVPD0 = amin1(AgsVPD(jent,1) * 0. + AgsVPD(jent,2), fgsVPDt)
  gsVPD0 = gsmax * fgsPAR * fgsCA * fgsLT * fgsVPD0

  fgsVPDair = amin1(amax1(AgsVPD(jent,1) * VPDair + AgsVPD(jent,2) , 0.05), fgsVPDt)
  gsVPDair = gsmax * fgsPAR * fgsCA * fgsLT * fgsVPDair

  gsi=0.5*(sqrt((ga-gsVPD0)**2+4.*ga*gsVPDair) - (ga-gsVPD0) )
  rsi=1/gsi


!  Step #6: Derivative of gs with regard to leaf temperature
!  Analytical solution, as found in SAFE booklet (H. Sinoquet, 23 dec 2002)

!  Derivative of fgsts with regard to leaf temperature
  select case (i_gsLT(jent))    ! type of equation for gs response to leaf temperature
   case (1) ! gs=f(leaf_temp) : 2nd order polynomial function
    dfgsLT=2*AgsLT(jent,1)*leaf_temp+AgsLT(jent,2)
    if (fgsLT.le.0.05) then
     dfgsLT=0.
    endif
   case default
    dfgsLT=0.
  end select

!  Derivative of gsVPD0 with regard to leaf temperature
  dgsVPD0=gsvpd0*dfgsLT/fgsLT

!  Saturating water vapor pressure, es, at temperature ts: Tetens' formula (1930), en Pa
!  and its derivative des, with regard to temperature ts
!  es=610.78*exp((17.27*leaf_temp)/(237.3+leaf_temp))
  des=610.78*17.27*237.3/((237.3+leaf_temp)**2)*exp((17.27*leaf_temp)/(237.3+leaf_temp))
!  Note that des is needed, as it it also the derivative of VPDair with regard to leaf temperature

!  Derivative of gsVPDair with regard to leaf temperature
  dfgsVPDair=AgsVPD(jent,1)*des
  if ((fgsVPDair.gt.0.05).and.(VPDair.gt.VPDthreshold)) then
   dgsVPDair=gsVPDair*(dfgsLT/fgsLT + dfgsVPDair/fgsVPDair)
  else
   dgsVPDair=gsVPDair*(dfgsLT/fgsLT)
  endif


  dgsi=sqrt((ga-gsVPD0)**2+4.*ga*gsVPDair)
  dgsi=0.5*(2.*dgsVPD0*(gsVPD0-ga)+4.*ga*dgsVPDair)/dgsi
  dgsi=0.5*(dgsVPD0+dgsi)

  drsi = - dgsi / gsi**2


 end subroutine Jarvis_stomata

 subroutine eb_destroy

  if (allocated(E_vt_vx))  deallocate(E_vt_vx)
  if (allocated(E_vx))   deallocate(E_vx)
  if (allocated(E_vt))   deallocate(E_vt)
  if (allocated(E_ss_vt))  deallocate(E_ss_vt)

  if (allocated(ts))   deallocate(ts)
  if (allocated(gs))   deallocate(gs)
  if (allocated(rco2))   deallocate(rco2)

  if (allocated(Sts))   deallocate(Sts)

 end subroutine eb_destroy

end module Energy_balance

!------------------------------------------------------------------------------
