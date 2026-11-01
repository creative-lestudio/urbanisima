#!/usr/bin/env python3
"""
Genera las páginas de servicios (/servicios/ y una página por servicio), el sitemap y las
redirecciones 301 de las URLs antiguas de WordPress.

Uso (desde la raíz del proyecto):   python3 scripts/build-services.py

Para cambiar un texto, edita SERVICES más abajo y vuelve a ejecutar el script.
Los textos parten de lo que ya decía la web antigua del cliente.
"""
import html, json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SITE = 'https://grupo-urbanisima.com'
PHONE_TXT = '+34 722 115 251'
PHONE_TEL = '+34722115251'
WA = '34722115251'
MAIL = 'info@grupo-urbanisima.com'
V = '28'  # versión de CSS/JS (rompe la caché del navegador)

# ---------------------------------------------------------------- DATOS
# rank = (particulares, comunidades, empresas): 1 = más solicitado. Debe coincidir con index.html.
SERVICES = [
 dict(key='tejados', slug='reparacion-de-tejados-valencia', icon='roof', rank=(1,3,2),
  title='Reparación de tejados y cubiertas',
  short='Cambio de tejas de pizarra o mixta y sustitución de tejas o uralita en tejados con humedades.',
  meta='Reparación de tejados y cubiertas en toda la provincia de Valencia: cambio de tejas, uralita, retejados e impermeabilización. Presupuesto gratis.',
  intro='Reparamos tejados y cubiertas en todas las localidades de la provincia de Valencia. Resolvemos goteras, tejas rotas o desplazadas y humedades, y renovamos la cubierta cuando hace falta, en viviendas, comunidades de vecinos y naves.',
  incluye=['Cambio de tejas de pizarra, tejas mixtas y otros tipos de teja','Retejados y recolocación de tejas desplazadas','Sustitución de uralita y de cubiertas deterioradas','Impermeabilización del tejado y sellado de filtraciones','Instalación de panel sandwich y aislamiento térmico','Montaje y limpieza de canalones y bajantes','Instalación de Velux y trabajos en azoteas'],
  senales=['Goteras o manchas de humedad en el techo cuando llueve','Tejas rotas, sueltas o desplazadas tras el viento o la lluvia','Cubierta de uralita antigua o deteriorada','Canalones obstruidos o que desbordan'],
  faq=[('¿Cómo sé si hay que reparar o renovar la cubierta?','Depende del estado de las tejas, de la estructura y de la antigüedad de la cubierta. En la visita sin coste la revisamos y te explicamos si basta una reparación puntual o conviene una renovación.'),
       ('¿Cuánto cuesta reparar un tejado?','Depende de la superficie, el material y el acceso. Por eso hacemos una visita sin coste y te damos un presupuesto sin compromiso.'),
       ('¿Trabajáis en comunidades de vecinos y naves industriales?','Sí. Atendemos a particulares, comunidades de vecinos, empresas y naves industriales en toda la provincia de Valencia.')],
  rel=['impermeabilizacion','canalones','panel']),
 dict(key='impermeabilizacion', slug='impermeabilizacion-terrazas-cubiertas-valencia', icon='drop', rank=(2,1,1),
  title='Impermeabilización de terrazas y cubiertas',
  short='Terrazas, azoteas, terrados, tejados y cubiertas. Fin de goteras y filtraciones.',
  meta='Impermeabilización de terrazas, azoteas y cubiertas en Valencia con resinas reforzadas con fibra de vidrio. Soluciones a goteras y humedades. Presupuesto gratis.',
  intro='Acabamos con las goteras, humedades y filtraciones en terrazas, azoteas, terrados, tejados y cubiertas. Una impermeabilización bien hecha evita que el agua siga entrando y que el daño llegue a la estructura del edificio.',
  incluye=['Revisión de la terraza o cubierta y localización del origen de la filtración','Reparación de grietas, fisuras y zonas deterioradas','Impermeabilización con resinas reforzadas con fibra de vidrio: flexibles, resistentes a la intemperie y transitables','Tratamiento de juntas, remates, bajantes y desagües','Impermeabilización de cubiertas de naves industriales','Mantenimiento y limpieza de canalones para prevenir humedades'],
  senales=['Humedad o manchas en techos y paredes bajo la terraza','Charcos que se acumulan o pintura que se levanta','Grietas o fisuras en el suelo de la terraza o azotea','Goteras que reaparecen tras reparaciones anteriores'],
  faq=[('¿Qué es una impermeabilización con resina reforzada con fibra de vidrio?','Es un revestimiento continuo y flexible que se aplica sobre la superficie y la protege del agua. Resiste la intemperie, es transitable y no suele requerir grandes obras. En la visita valoramos si es la solución adecuada en tu caso.'),
       ('¿Por qué vuelve a entrar el agua si ya reparé la terraza?','Si la impermeabilización no se hace correctamente, la humedad sigue entrando y provoca daños mayores. Hay que localizar el origen real de la filtración y tratar toda la superficie y los remates.'),
       ('¿Cuánto cuesta impermeabilizar una terraza o cubierta?','Depende de la superficie, el estado del soporte y los remates. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['tejados','canalones','panel']),
 dict(key='canalones', slug='canalones-valencia', icon='gutter', rank=(3,5,5),
  title='Montaje y limpieza de canalones',
  short='Limpieza, mantenimiento y cambio total de canalones, canaletas y bajantes.',
  meta='Montaje, limpieza y mantenimiento de canalones, canaletas y bajantes en Valencia: aluminio, zinc, cobre y galvanizados. Presupuesto gratis y sin compromiso.',
  intro='Instalamos, limpiamos y mantenemos canalones pluviales, canaletas y bajantes de todo tipo: aluminio, zinc, cobre o galvanizados. Un canalón en mal estado es una de las causas más habituales de filtraciones en cubiertas y tejados. Todo el equipo cumple la normativa de prevención de riesgos laborales.',
  incluye=['Limpieza de canalones, canaletas y bajantes','Montaje y sustitución completa de canalones','Revisión y mantenimiento periódico','Canalones de aluminio, zinc, cobre y galvanizados','Corrección de pendientes para que no acumulen agua','Sistemas antipájaros'],
  senales=['Canalones que desbordan o gotean cuando llueve','Hojas, barro o suciedad acumulados','Canalones oxidados, deformados o despegados','Manchas de humedad en la fachada bajo el canalón'],
  faq=[('¿Cada cuánto conviene limpiar los canalones?','Conviene revisarlos antes de la temporada de lluvias y después de temporales, sobre todo si hay árboles cerca, que acumulan hojas y suciedad.'),
       ('¿Hacéis el trabajo con andamio?','Hacemos trabajos en altura con o sin andamios, según lo que requiera cada caso.'),
       ('¿Cuánto cuesta limpiar o cambiar un canalón?','Depende de la longitud, el material y el acceso. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['tejados','impermeabilizacion','verticales']),
 dict(key='fachadas', slug='pintura-rehabilitacion-fachadas-valencia', icon='brush', rank=(4,2,10),
  title='Pintura y rehabilitación de fachadas',
  short='Fachadas, patios interiores, garajes y parkings, casas y chalets. Trabajos verticales o con andamios.',
  meta='Pintura y rehabilitación de fachadas, patios interiores, portales, casas y chalets en Valencia. Trabajos verticales sin andamio. Presupuesto gratis y sin compromiso.',
  intro='Pintamos y rehabilitamos fachadas, patios interiores, portales, casas y chalets. Como especialistas en trabajos verticales, accedemos sin andamios a los puntos más difíciles, de forma rápida, segura y sin molestar a propietarios e inquilinos. Contamos además con asesoramiento de decoración y pintura.',
  incluye=['Pintura exterior y rehabilitación de fachadas','Pintura y restauración de patios interiores','Pintura de portales: techos, paredes, escaleras, rellanos, barandillas, rejas y puertas','Pintura interior y exterior de viviendas y chalets: plástica, alisados, estucos, quitar gotelé, papel pintado, barnizados y lacados','Pintado de garajes y parkings','Trabajos con andamio o con descuelgue vertical'],
  senales=['Pintura desconchada, sucia o descolorida','Humedades, grietas o desprendimientos en la fachada','Patio interior deteriorado o con manchas','Quieres renovar el aspecto de tu casa o de tu comunidad'],
  faq=[('¿Hace falta montar andamios?','No siempre. Con trabajos verticales (descuelgue) accedemos a muchos puntos sin andamio, con menos molestias para los vecinos. Lo valoramos en la visita sin coste.'),
       ('¿Qué materiales utilizáis?','Materiales de primera calidad, con certificado de calidad de los fabricantes, para garantizar un buen acabado.'),
       ('¿Cuánto cuesta pintar una fachada o un patio?','Depende de la superficie, la altura, el estado del soporte y el tipo de acceso. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['verticales','garajes','impermeabilizacion']),
 dict(key='verticales', slug='trabajos-verticales-valencia', icon='tools', rank=(9,4,4),
  title='Trabajos verticales y en altura',
  short='Con o sin andamios, en toda la provincia de Valencia.',
  meta='Trabajos verticales y en altura en Valencia, con o sin andamios: fachadas, patios, cubiertas y canalones de difícil acceso. Presupuesto gratis.',
  intro='Realizamos trabajos en altura, con o sin andamios, en toda la provincia de Valencia. Con el descuelgue vertical llegamos a fachadas, patios interiores, cubiertas y otros puntos de difícil acceso de forma rápida y segura, sin molestar a propietarios e inquilinos.',
  incluye=['Acceso por descuelgue vertical, sin necesidad de andamios','Pintura y rehabilitación de fachadas y patios interiores','Reparación y limpieza en cubiertas y canalones de difícil acceso','Saneado y retirada o fijación de elementos sueltos con riesgo de caída','Presentación de plan de trabajo y de seguridad'],
  senales=['Patios interiores o fachadas de difícil acceso','Elementos sueltos o desprendimientos con riesgo de caída','Cubiertas o canalones que no se alcanzan sin medios especiales','Quieres evitar el coste y las molestias de un andamio'],
  faq=[('¿Qué es un trabajo vertical?','Es un trabajo en altura en el que los operarios acceden mediante cuerdas (descuelgue) en lugar de montar andamios. Es una opción adecuada para zonas de difícil acceso.'),
       ('¿Es seguro?','Presentamos plan de trabajo y de seguridad, y la documentación laboral y legal de nuestros trabajadores.'),
       ('¿Cuánto cuesta un trabajo en altura?','Depende de la altura, el tipo de trabajo y el acceso. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['fachadas','canalones','tejados']),
 dict(key='garajes', slug='pintura-garajes-parkings-valencia', icon='brush', rank=(10,6,11),
  title='Pintado de garajes y parkings',
  short='Renovación de garajes, parkings y zonas comunes.',
  meta='Pintado de garajes y parkings en Valencia para comunidades de vecinos y empresas: paredes, techos y pavimento con pintura epoxi. Presupuesto gratis y sin compromiso.',
  intro='Renovamos garajes, parkings y zonas comunes de comunidades de vecinos, empresas y particulares. Cada garaje es distinto: en la visita valoramos el estado del suelo y de las paredes y te proponemos la mejor solución.',
  incluye=['Pintura de paredes, techos y elementos del garaje o parking','Pintura epoxi en el pavimento','Trabajos con medios de elevación o descuelgue vertical cuando hace falta','Coordinación con la comunidad o la empresa para organizar el trabajo'],
  senales=['Paredes o techos desconchados, sucios o con manchas','Suelo de hormigón desgastado o con manchas de aceite','Quieres renovar un garaje comunitario o un parking de empresa'],
  faq=[('¿Pintáis también el suelo del garaje?','Sí. Para el pavimento utilizamos pintura epoxi, que da una superficie lisa, fácil de limpiar y que ayuda a prevenir las manchas de aceite.'),
       ('¿Trabajáis para comunidades de vecinos?','Sí. Atendemos a comunidades de vecinos, empresas y particulares en toda la provincia de Valencia.'),
       ('¿Cuánto cuesta pintar un garaje?','Depende de la superficie y del estado de las paredes y del suelo. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['epoxi','fachadas','reformas']),
 dict(key='panel', slug='panel-sandwich-valencia', icon='layers', rank=(11,7,3),
  title='Panel sandwich',
  short='Aislante térmico y acústico, impermeabilizante. Montaje e instalación.',
  meta='Instalación y montaje de panel sandwich en Valencia: cubiertas con aislamiento térmico y acústico para viviendas y naves. Presupuesto gratis.',
  intro='Instalamos, rehabilitamos y mantenemos paneles sandwich en toda la provincia de Valencia. Es una solución ideal tanto para naves industriales como para viviendas: impermeabiliza y aporta aislamiento térmico y acústico, resistente y duradero.',
  incluye=['Montaje de panel sandwich sobre la cubierta existente, formando una doble capa','Sustitución de la cubierta existente por placas de panel sandwich, evitando sobrepeso','Cubiertas tipo sándwich y paneles de policarbonato','Rehabilitación y mantenimiento de paneles','Limpieza y mantenimiento de paneles de aluminio, cobre o galvanizados'],
  senales=['Cubierta de nave o vivienda con goteras o mal aislamiento','Problemas de temperatura o de ruido bajo la cubierta','Uralita o cubierta antigua que conviene sustituir'],
  faq=[('¿Se puede instalar sobre la cubierta que ya tengo?','Sí, en muchos casos el panel sandwich se instala sobre la cubierta existente, formando una doble capa. También puede sustituirla para evitar sobrepeso. Lo valoramos en la visita.'),
       ('¿Sirve para viviendas o solo para naves?','Sirve para ambos: es una solución habitual en edificios industriales y también en viviendas.'),
       ('¿Cuánto cuesta instalar panel sandwich?','Depende de la superficie, el tipo de panel y el acceso. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['tejados','impermeabilizacion','epoxi']),
 dict(key='epoxi', slug='pavimentos-continuos-epoxi-valencia', icon='floor', rank=(13,9,6),
  title='Pavimentos continuos y epoxi',
  short='Pintura epoxi en pavimento continuo para naves, locales y garajes.',
  meta='Pavimentos continuos y pintura epoxi en Valencia para naves, talleres, almacenes, garajes y trasteros: suelo liso, antideslizante y fácil de limpiar. Presupuesto gratis.',
  intro='Aplicamos pintura epoxi en pavimento continuo para dar un nuevo aspecto a suelos de hormigón deteriorados. Obtienes una superficie lisa, coloreada e incluso antideslizante, más fácil de limpiar y que ayuda a prevenir las manchas de derrames de aceite.',
  incluye=['Pintura epoxi bicomponente en suelos de hormigón','Superficies lisas, coloreadas o antideslizantes','Naves industriales, talleres, almacenes, garajes, sótanos y trasteros','Pintura de naves por el interior y por el exterior, con medios de elevación y aplicación airless','Saneado, retirada o aseguramiento de elementos sueltos en la pintura exterior'],
  senales=['Suelo de hormigón desgastado, polvoriento o con manchas','Pavimento de taller o nave deteriorado','Manchas de aceite difíciles de limpiar','Quieres un suelo más fácil de limpiar y con mejor aspecto'],
  faq=[('¿Para qué locales sirve el pavimento epoxi?','Es útil para talleres y naves, y también para almacenes, garajes, sótanos y trasteros.'),
       ('¿Se puede hacer antideslizante?','Sí, el acabado puede ser liso, coloreado o antideslizante. Lo definimos contigo en la visita según el uso del suelo.'),
       ('¿Cuánto cuesta un pavimento epoxi?','Depende de la superficie, el estado del hormigón y el acabado. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['garajes','panel','fachadas']),
 dict(key='chimeneas', slug='deshollinado-chimeneas-valencia', icon='flame', rank=(5,12,14),
  title='Deshollinado de chimeneas',
  short='Limpieza y deshollinación de chimeneas.',
  meta='Limpieza y deshollinado de chimeneas en Valencia: elimina hollín, creosota y cenizas, y previene incendios e intoxicaciones. Presupuesto gratis y sin compromiso.',
  intro='Una chimenea mal mantenida supone un riesgo de incendio. La combustión de la leña genera hollín, creosota y cenizas que se acumulan en la chimenea y en el conducto de humos. Deshollinar protege frente a incendios y también frente a intoxicaciones.',
  incluye=['Limpieza y deshollinado de la chimenea y del conducto de humos','Eliminación de hollín, creosota, cenizas y suciedad','Revisión periódica de la chimenea','Recomendaciones de uso y mantenimiento'],
  senales=['Humo que no sale bien o vuelve a la vivienda','Olor a humo o a quemado, o hollín acumulado','Llevas tiempo sin limpiar la chimenea','Vas a empezar la temporada de uso'],
  faq=[('¿Por qué es importante deshollinar?','Si el conducto está obstruido, los gases se quedan dentro de la vivienda, lo que puede ser peligroso. Además, la creosota acumulada aumenta el riesgo de incendio.'),
       ('¿Qué puedo hacer yo para cuidarla?','Limpiar las cenizas del hogar con regularidad y quemar solo leña adecuada. Aun así, conviene no renunciar al mantenimiento por parte de un profesional.'),
       ('¿Cuánto cuesta deshollinar una chimenea?','Depende del tipo de chimenea y del acceso. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['tejados','canalones','reformas']),
 dict(key='jardines', slug='jardineria-diseno-jardines-valencia', icon='leaf', rank=(7,10,12),
  title='Jardinería y diseño de jardines',
  short='Diseño y mantenimiento de jardines, y mantenimiento de piscinas.',
  meta='Jardinería y diseño de jardines en Valencia: mantenimiento, podas, talas, desbroces, césped artificial y diseño a medida. Presupuesto gratis y sin compromiso.',
  intro='Realizamos todo tipo de trabajos de jardinería con la maquinaria adecuada para cada labor: mantenimiento, podas, talas, desbroces y limpiezas, césped artificial y diseño de jardines. Tú nos cuentas qué idea tienes y nosotros la hacemos realidad.',
  incluye=['Mantenimiento de jardines','Podas y talas','Desbroces y limpiezas','Instalación de césped artificial','Diseño de jardines: especies florales, árboles, arbustos y césped natural o artificial','Elementos ornamentales: fuentes, piedras o estatuas'],
  senales=['Jardín descuidado o con maleza','Árboles o setos que necesitan poda o tala','Quieres renovar o diseñar un jardín nuevo','Prefieres césped artificial y menos mantenimiento'],
  faq=[('¿Puedo elegir las plantas y los elementos del jardín?','Sí. Puedes elegir las especies florales, árboles, arbustos, tipo de césped y elementos ornamentales, y nos encargamos de llevarlo a cabo.'),
       ('¿Hacéis también mantenimiento periódico?','Sí, realizamos trabajos de mantenimiento, podas, talas, desbroces y limpiezas.'),
       ('¿Cuánto cuesta diseñar o mantener un jardín?','Depende de la superficie y del trabajo. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['piscinas','reformas','fachadas']),
 dict(key='piscinas', slug='mantenimiento-piscinas-valencia', icon='drop', rank=(8,11,13),
  title='Mantenimiento de piscinas',
  short='Mantenimiento y limpieza de piscinas.',
  meta='Mantenimiento y limpieza de piscinas en Valencia, y rehabilitación cuando hace falta. Presupuesto gratis y sin compromiso.',
  intro='Mantenemos y limpiamos piscinas de viviendas y chalets en la provincia de Valencia, y valoramos su rehabilitación cuando el estado del vaso lo requiere. Cuéntanos qué necesitas y lo revisamos en una visita sin coste.',
  incluye=['Mantenimiento y limpieza de la piscina','Revisión del estado del vaso','Valoración de reparaciones y rehabilitación cuando hacen falta'],
  senales=['Piscina con suciedad, algas o mal aspecto','Piscina sin usar durante un tiempo','Sospecha de fugas, grietas o desperfectos en el vaso'],
  faq=[('¿Rehabilitáis piscinas?','Valoramos la rehabilitación según el estado de la piscina. Lo revisamos en la visita sin coste y te explicamos las opciones.'),
       ('¿Atendéis a comunidades y empresas?','Sí. Atendemos a particulares, comunidades de vecinos y empresas en toda la provincia de Valencia.'),
       ('¿Cuánto cuesta el mantenimiento de una piscina?','Depende del tamaño y del trabajo necesario. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['jardines','impermeabilizacion','reformas']),
 dict(key='locales', slug='reformas-integrales-locales-valencia', icon='tools', rank=(12,13,7),
  title='Reformas integrales de locales',
  short='Reformas de locales y comercios.',
  meta='Reformas integrales de locales y comercios en Valencia con todos los gremios coordinados: albañilería, fontanería, electricidad, pintura y suelos. Presupuesto gratis.',
  intro='Si has adquirido un local o quieres mejorar el que tienes, cuéntanos qué idea tienes y qué imagen quieres proyectar de tu negocio. Contamos con los gremios necesarios y los coordinamos para cumplir los plazos acordados.',
  incluye=['Solados y alicatados','Pintura','Instalación de puertas, ventanas y suelos','Instalaciones eléctricas y de fontanería','Asesoramiento sobre materiales y distribución óptima de los espacios','Impermeabilización y reparación de humedades del edificio'],
  senales=['Local recién adquirido que necesita adaptarse a tu negocio','Quieres renovar la imagen de tu local o comercio','Instalaciones antiguas, humedades o suelos deteriorados'],
  faq=[('¿Os encargáis de todos los gremios?','Sí. Contamos con profesionales de los distintos gremios y los coordinamos para que la reforma avance según los plazos acordados.'),
       ('¿Me asesoráis con los materiales y la distribución?','Sí. Te asesoramos sobre los materiales más adecuados y sobre la distribución más óptima de los espacios.'),
       ('¿Cuánto cuesta reformar un local?','Depende de la superficie y del alcance de la reforma. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['reformas','cocinas','epoxi']),
 dict(key='cocinas', slug='mantenimiento-cocinas-industriales-valencia', icon='tools', rank=(14,14,8),
  title='Mantenimiento de cocinas industriales',
  short='Mantenimiento para cocinas de empresas y comercios.',
  meta='Mantenimiento de cocinas industriales en Valencia para empresas y comercios. Cuéntanos qué necesitas y te damos presupuesto gratis y sin compromiso.',
  intro='Ofrecemos mantenimiento de cocinas industriales para empresas y comercios de la provincia de Valencia. Cada cocina tiene necesidades distintas: cuéntanos qué necesitas y lo valoramos en una visita sin coste.',
  incluye=['Mantenimiento de cocinas industriales de empresas y comercios','Reformas y mejoras en suelos, alicatados y pintura del local','Valoración personalizada según las necesidades de cada cocina'],
  senales=['Cocina industrial con desgaste o desperfectos','Necesitas mantenimiento periódico para tu negocio','Quieres reformar la zona de cocina de tu local'],
  faq=[('¿Qué incluye el mantenimiento?','Depende de las necesidades de cada cocina. Por eso empezamos con una visita sin coste para valorar qué hace falta y plantearte un presupuesto.'),
       ('¿Hacéis también la reforma del local?','Sí, realizamos reformas integrales de locales con los gremios necesarios.'),
       ('¿Cuánto cuesta?','Depende del trabajo y del tamaño de la cocina. Hacemos una visita sin coste y te damos un presupuesto sin compromiso.')],
  rel=['locales','reformas','epoxi']),
 dict(key='reformas', slug='reformas-valencia', icon='tools', rank=(6,8,9),
  title='Reformas en general',
  short='Todo tipo de reformas: canalización de agua, Velux y azoteas.',
  meta='Reformas en Valencia para viviendas, pisos, casas y locales: cocinas, baños, albañilería, fontanería, electricidad, pintura y más. Presupuesto gratis y sin compromiso.',
  intro='Realizamos reformas integrales y parciales de viviendas, pisos, casas y locales comerciales. Planificamos presupuestos consensuados según las necesidades de cada cliente, te asesoramos en cada paso del proyecto y damos garantía de nuestro trabajo.',
  incluye=['Reformas integrales de viviendas, pisos, casas y locales','Reformas de cocinas y baños','Puertas, ventanas y cerramientos','Pintura','Fontanería, electricidad y canalización de agua','Albañilería, alicatados y solados, escayola y pladur','Instalación de Velux y trabajos en azoteas'],
  senales=['Vivienda o local que necesita renovarse','Cocina o baño anticuados','Instalaciones antiguas de agua o electricidad','Quieres una reforma con un único interlocutor y comunicación constante'],
  faq=[('¿Hacéis reformas integrales?','Sí: reformas integrales de viviendas, pisos, casas y locales, así como reformas parciales de una cocina, un baño u otras estancias.'),
       ('¿Cómo se plantea el presupuesto?','Planificamos presupuestos consensuados en función de las necesidades de cada cliente, tras una visita sin coste.'),
       ('¿Dais garantía del trabajo?','Sí. Los trabajos cuentan con la garantía legal que corresponde y con la que se indique en el presupuesto.')],
  rel=['locales','fachadas','jardines']),
]
BITS = {
 'tejados': ['Cambio de tejas y uralita', 'Retejados y goteras', 'Panel sandwich y Velux'],
 'impermeabilizacion': ['Resinas con fibra de vidrio', 'Terrazas, azoteas y naves', 'Fin de goteras y humedades'],
 'canalones': ['Limpieza y bajantes', 'Montaje y sustitución', 'Aluminio, zinc y cobre'],
 'fachadas': ['Fachadas y patios interiores', 'Portales y comunidades', 'Casas y chalets'],
 'verticales': ['Sin andamios (descuelgue)', 'Plan de seguridad', 'Fachadas y cubiertas'],
 'garajes': ['Paredes y techos', 'Pavimento epoxi', 'Comunidades y empresas'],
 'panel': ['Doble capa o sustitución', 'Aislamiento térmico y acústico', 'Naves y viviendas'],
 'epoxi': ['Suelo liso y antideslizante', 'Naves, talleres y garajes', 'Fácil de limpiar'],
 'chimeneas': ['Hollín y creosota', 'Prevención de incendios', 'Revisión periódica'],
 'jardines': ['Podas, talas y desbroces', 'Césped artificial', 'Diseño de jardines'],
 'piscinas': ['Mantenimiento y limpieza', 'Revisión del vaso', 'Rehabilitación'],
 'locales': ['Todos los gremios', 'Solados y alicatados', 'Electricidad y fontanería'],
 'cocinas': ['Empresas y comercios', 'Mantenimiento', 'Reformas de cocina'],
 'reformas': ['Viviendas y locales', 'Cocinas y baños', 'Fontanería y electricidad'],
}
for _s in SERVICES: _s['bits'] = BITS[_s['key']]
PROBLEMS = [  # icono, título, subtítulo, servicio al que lleva
 ('drop', 'Goteras en el techo', 'Humedades y filtraciones', 'impermeabilizacion'),
 ('roof', 'Tejado deteriorado', 'Tejas rotas o cubierta antigua', 'tejados'),
 ('gutter', 'Canalones obstruidos', 'Limpieza o cambio', 'canalones'),
 ('brush', 'Fachada o patio', 'Pintura y rehabilitación', 'fachadas'),
 ('layers', 'Cubierta de nave', 'Panel sandwich y aislamiento', 'panel'),
 ('floor', 'Suelo de nave o garaje', 'Pavimento epoxi', 'epoxi'),
 ('flame', 'Chimenea', 'Limpieza y deshollinado', 'chimeneas'),
 ('tools', 'Reforma', 'Viviendas y locales', 'reformas'),
]
BY_KEY = {s['key']: s for s in SERVICES}

# Redirecciones 301: URL antigua de WordPress -> página nueva (sin barra inicial ni final)
OLD = {
 'tejados': ['rehabilitacion-de-tejados-en-valencia','reparacion-de-tejados-en-valencia','reparacion-y-rehabilitacion-de-cubiertas-en-valencia','reparacion-cubiertas-naves-industriales-valencia','servicios-grupo-urbanisima/servicios-de-reparacion-de-tejados'],
 'impermeabilizacion': ['impermeabilizacion-de-tejados-en-valencia','impermeabilizacion-de-terrazas-en-valencia','rehabilitacion-de-terrazas-en-valencia','impermeabilizacion-de-cubiertas-en-valencia','especialistas-en-impermeabilizacion-en-valencia','impermeabilizacion-de-cubiertas-valencia','servicios-grupo-urbanisima/servicios-de-impermeabilizacion-de-cubiertas','servicios-grupo-urbanisima/servicios-de-impermeabilizacion-de-terrazas'],
 'canalones': ['instalacion-y-montaje-de-canalones-en-valencia','limpieza-y-mantenimiento-de-canalones','impermeabilizacion-y-reparacion-de-canalones','servicios-grupo-urbanisima/servicios-de-limpieza-de-canalones'],
 'panel': ['instalacion-y-montaje-de-panel-sandwich','servicios-grupo-urbanisima/servicios-de-montaje-de-panel-sandwich'],
 'chimeneas': ['limpieza-y-deshollinado-de-chimenea-en-valencia','limpieza-y-deshollinado-de-chimenea-en-alicante','limpieza-y-deshollinado-de-chimenea-en-castellon','especialistas-en-deshollinar-chimeneas','deshollinacion-de-chimeneas-en-alicante','deshollinacion-de-chimeneas-en-castellon','servicios-grupo-urbanisima/servicio-de-limpieza-y-deshollinado-de-chimenea'],
 'epoxi': ['servicios-grupo-urbanisima/servicio-de-pintura-epoxi-en-pavimento-continuo'],
 'fachadas': ['servicios-grupo-urbanisima/servicios-de-pintores-de-casas-y-chalets-particulares-en-valencia','servicios-grupo-urbanisima/servicios-de-pintores-de-fachadas-y-patios-interiores'],
 'jardines': ['servicios-grupo-urbanisima/servicios-de-jardineria','diseno-de-jardines-valencia'],
 'piscinas': ['servicios-grupo-urbanisima/servicios-de-rehabilitacion-y-limpieza-de-piscinas-en-valencia'],
 'reformas': ['servicios-grupo-urbanisima/servicios-de-reformas'],
 'locales': ['reformas-integrales-de-locales-valencia'],
}
OTHER_REDIRECTS = {  # destino directo
 'servicios-grupo-urbanisima': '/servicios/',
 'contactar': '/?ir=contacto',
 'servicios-a-particulares': '/?perfil=particulares&ir=servicios',
 'servicios-a-comunidades-de-vecinos': '/?perfil=comunidades&ir=servicios',
 'servicios-a-empresas-comercios-y-naves-industriales': '/?perfil=empresas&ir=servicios',
}
# Aire acondicionado: la web nueva no lo incluye. Mientras el cliente decide, va a la portada.
OLD_AC = ['recarga-de-aires-acondicionados-en-valencia','servicios-grupo-urbanisima/recarga-de-aires-acondicionados','servicios-de-montaje-e-instalacion-de-aire-acondicionado-en-valencia','reparacion-de-aire-acondicionado-en-valencia']

# ---------------------------------------------------------------- PLANTILLAS
e = html.escape
def ic(name, root, cls='i'): return f'<svg class="{cls}"><use href="{root}assets/icons.svg#i-{name}"/></svg>'

def head(title, desc, canonical, root, extra=''):
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="Grupo Urbanísima">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta name="theme-color" content="#01335a">
<link rel="icon" href="{root}assets/logo.png">
<link rel="preload" href="{root}assets/fonts/montserrat-latin-variable.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{root}assets/fonts/fonts.css">
<style>.i{{width:1.15em;height:1.15em;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:none}}.skip{{position:absolute;left:-999px;top:8px}}</style>
<link rel="stylesheet" href="{root}styles.css?v={V}">
<script src="{root}config.js?v={V}"></script>
<script src="{root}tracking.js?v={V}" defer></script>
<script src="{root}pages.js?v={V}" defer></script>
{extra}</head>
'''

def header(root):
    return f'''<a class="skip" href="#contenido">Saltar al contenido</a>
<header class="header solid" id="top">
  <div class="wrap nav">
    <a href="{root}" class="brand" aria-label="Grupo Urbanísima, inicio"><img class="logo-color" src="{root}assets/logo.png" alt="" width="268" height="55"><img class="logo-white" src="{root}assets/logo-blanco.png" alt="" width="260" height="51"></a>
    <nav id="menu" class="menu" aria-label="Principal">
      <a href="{root}">Inicio</a>
      <a href="{root}servicios/">Servicios</a>
      <a href="#contacto">Contacto</a>
      <a href="tel:{PHONE_TEL}" class="menu-phone">{ic('phone',root)}722 115 251</a>
      <a href="#contacto" class="btn btn-sm">Pedir presupuesto</a>
    </nav>
    <button class="burger" aria-label="Abrir menú" aria-expanded="false" aria-controls="menu"><span></span><span></span></button>
  </div>
</header>
'''

RGPD = '''<details class="rgpd"><summary>Información básica sobre protección de datos</summary>
        <dl>
          <dt>Responsable</dt><dd>Grupo Urbanisima S.L.U.</dd>
          <dt>Finalidad</dt><dd>Atender tu solicitud de presupuesto o consulta.</dd>
          <dt>Legitimación</dt><dd>Tu consentimiento y las medidas precontractuales que nos pides.</dd>
          <dt>Destinatarios</dt><dd>No cedemos datos a terceros salvo obligación legal. Usamos proveedores de alojamiento y correo y, si eliges WhatsApp, esa plataforma (Meta). Con WhatsApp también recibimos una copia por correo.</dd>
          <dt>Derechos</dt><dd>Acceso, rectificación, supresión, oposición, limitación y portabilidad, escribiendo a info@grupo-urbanisima.com. Puedes reclamar ante la AEPD.</dd>
          <dt>Más información</dt><dd><a href="{root}ley-proteccion-datos/" target="_blank" rel="noopener">Política de privacidad</a></dd>
        </dl>
      </details>'''

def contact_section(root, heading, service_title=None):
    if service_title:
        svc = f'<input type="hidden" name="servicio" value="{e(service_title)}">'
    else:
        opts = ''.join(f'<option>{e(s["title"])}</option>' for s in SERVICES)
        svc = f'<div class="field"><label for="c-serv">¿Qué necesitas?</label><select id="c-serv" name="servicio"><option value="">Selecciona un servicio</option>{opts}<option>Otro</option></select></div>'
    return f'''<section class="section contact" id="contacto">
  <div class="wrap split">
    <div class="contact-copy">
      <p class="eyebrow">Contacto</p>
      <h2>{e(heading)}</h2>
      <p class="lead">Visita a domicilio sin coste y presupuesto sin compromiso, en toda la provincia de Valencia. Te respondemos en menos de 24 horas.</p>
      <ul class="contact-list">
        <li><a href="tel:{PHONE_TEL}"><span class="ico">{ic('phone',root)}</span><span><small>Llámanos</small>{PHONE_TXT}</span></a></li>
        <li><a href="https://wa.me/{WA}?text=Hola%2C%20quiero%20pedir%20presupuesto" target="_blank" rel="noopener"><span class="ico">{ic('chat',root)}</span><span><small>WhatsApp</small>Escríbenos ahora</span></a></li>
        <li><a href="mailto:{MAIL}"><span class="ico">{ic('mail',root)}</span><span><small>Email</small>{MAIL}</span></a></li>
        <li><span class="row"><span class="ico">{ic('clock',root)}</span><span><small>Atención telefónica</small>Lunes a viernes, de 9:00 a 19:00</span></span></li>
      </ul>
    </div>
    <form class="card" id="contact-form" novalidate>
      <div class="card-head"><h2>Cuéntanos qué necesitas</h2><p>Elige cómo quieres enviarlo: por correo o por WhatsApp.</p></div>
      <div class="field"><label for="c-nombre">Nombre</label><input id="c-nombre" name="nombre" type="text" autocomplete="name" placeholder="Tu nombre" required></div>
      <div class="field-row">
        <div class="field"><label for="c-tel">Teléfono</label><input id="c-tel" name="telefono" type="tel" autocomplete="tel" inputmode="tel" placeholder="6XX XXX XXX" required></div>
        <div class="field"><label for="c-email">Correo <small>(opcional)</small></label><input id="c-email" name="email" type="email" autocomplete="email" inputmode="email" placeholder="tu@correo.com"></div>
      </div>
      <div class="field"><label for="c-perfil">Soy <small>(opcional)</small></label>
        <select id="c-perfil" name="perfil"><option value="">Selecciona</option><option>Particular</option><option>Comunidad de vecinos</option><option>Empresa / nave industrial</option></select></div>
      {svc}
      <div class="field"><label for="c-msg">Describe lo que necesitas</label>
        <textarea id="c-msg" name="mensaje" rows="4" required minlength="10" placeholder="Ej.: qué ocurre, dónde, metros aproximados y si es urgente…"></textarea>
        <p class="hint">Cuanto más detalle, mejor podremos valorar el servicio y darte un presupuesto ajustado.</p>
      </div>
      <div class="hp" aria-hidden="true"><label>Web <input name="web" tabindex="-1" autocomplete="off"></label></div>
      <label class="check"><input type="checkbox" name="privacidad" required> <span>He leído y acepto la <a href="{root}ley-proteccion-datos/" target="_blank" rel="noopener">política de privacidad</a></span></label>
      <div class="send-row">
        <button type="submit" name="canal" value="email" class="btn btn-mail">{ic('mail',root)} Enviar por correo</button>
        <button type="submit" name="canal" value="whatsapp" class="btn btn-wa">{ic('chat',root)} Enviar por WhatsApp</button>
      </div>
      <p class="send-note">Si lo envías por WhatsApp, también recibimos una copia en nuestro correo.</p>
      {RGPD.replace('{root}',root)}
      <p class="form-msg" role="status" aria-live="polite"></p>
    </form>
  </div>
</section>
'''

def footer(root):
    return f'''<footer class="site-foot">
  <div class="wrap foot-top">
    <div class="foot-brand">
      <img src="{root}assets/logo-blanco.png" alt="Grupo Urbanísima" width="260" height="51" loading="lazy">
      <p>Reparación de tejados, impermeabilización de terrazas y cubiertas, canalones y fachadas para particulares, comunidades de vecinos y empresas.</p>
      <div class="foot-cta">
        <a href="tel:{PHONE_TEL}" class="btn btn-sm">{ic('phone',root)} Llamar</a>
        <a href="https://wa.me/{WA}?text=Hola%2C%20quiero%20pedir%20presupuesto" class="btn btn-sm btn-wa" target="_blank" rel="noopener">{ic('chat',root)} WhatsApp</a>
      </div>
    </div>
    <nav class="foot-col" aria-label="Servicios">
      <h4>Servicios</h4>
      <a href="{root}servicios/">Todos los servicios</a>
      <a href="{root}servicios/{BY_KEY['tejados']['slug']}/">Reparación de tejados</a>
      <a href="{root}servicios/{BY_KEY['impermeabilizacion']['slug']}/">Impermeabilización</a>
      <a href="{root}servicios/{BY_KEY['canalones']['slug']}/">Canalones</a>
    </nav>
    <nav class="foot-col" aria-label="Más servicios">
      <h4>Más</h4>
      <a href="{root}servicios/{BY_KEY['fachadas']['slug']}/">Fachadas</a>
      <a href="{root}servicios/{BY_KEY['panel']['slug']}/">Panel sandwich</a>
      <a href="{root}servicios/{BY_KEY['chimeneas']['slug']}/">Chimeneas</a>
      <a href="{root}servicios/{BY_KEY['reformas']['slug']}/">Reformas</a>
    </nav>
    <div class="foot-col">
      <h4>Contacto</h4>
      <a href="tel:{PHONE_TEL}">{ic('phone',root)}{PHONE_TXT}</a>
      <a href="mailto:{MAIL}">{ic('mail',root)}{MAIL}</a>
      <span class="foot-note">{ic('check',root)}Servicio en toda la provincia de Valencia</span>
    </div>
  </div>
  <div class="wrap foot-legal">
    <div class="legal-left">
      <span>© <span id="year">2026</span> Grupo Urbanísima. Todos los derechos reservados.</span>
      <nav aria-label="Legal">
        <a href="{root}aviso-legal/">Aviso legal</a>
        <a href="{root}ley-proteccion-datos/">Privacidad</a>
        <a href="{root}aviso-ley-cookies/">Cookies</a>
        <a href="{root}condiciones/">Condiciones</a>
        <button type="button" class="link-btn" data-cookie-settings hidden>Configurar cookies</button>
      </nav>
    </div>
    <a class="sign" href="https://lestudio-crea.com" target="_blank" rel="noopener" aria-label="Desarrollado por Le Studio"><span>Desarrollado por</span><img src="{root}assets/lestudio-logo.png" alt="Le Studio" width="900" height="392" loading="lazy"></a>
  </div>
</footer>
<a class="fab" href="https://wa.me/{WA}?text=Hola%2C%20quiero%20pedir%20presupuesto" target="_blank" rel="noopener" aria-label="Escribir por WhatsApp">{ic('chat',root)}<span>WhatsApp</span></a>
<div class="sticky-cta">
  <a href="tel:{PHONE_TEL}" class="btn btn-ghost-dark">{ic('phone',root)} Llamar</a>
  <a href="https://wa.me/{WA}?text=Hola%2C%20quiero%20pedir%20presupuesto" class="btn btn-wa" target="_blank" rel="noopener">{ic('chat',root)} WhatsApp</a>
</div>
</body>
</html>
'''

def jsonld(graph):
    return '<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False) + '</script>\n'

PROVIDER = {'@type': 'LocalBusiness', 'name': 'Grupo Urbanísima', 'telephone': PHONE_TEL, 'email': MAIL, 'url': SITE + '/',
            'address': {'@type': 'PostalAddress', 'streetAddress': 'Calle Jacinto Labaila 8b', 'addressLocality': 'Valencia', 'addressCountry': 'ES'}}

def service_page(s):
    root = '../../'
    url = f'{SITE}/servicios/{s["slug"]}/'
    title = f'{s["title"]} en Valencia | Grupo Urbanísima'
    h1 = f'{s["title"]} en Valencia'
    graph = [
      {'@type': 'Service', 'name': s['title'], 'serviceType': s['title'], 'description': s['intro'], 'url': url, 'provider': PROVIDER,
       'areaServed': {'@type': 'AdministrativeArea', 'name': 'Provincia de Valencia'}},
      {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Servicios', 'item': SITE + '/servicios/'},
        {'@type': 'ListItem', 'position': 3, 'name': s['title'], 'item': url}]},
      {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in s['faq']]},
    ]
    inc = ''.join(f'<li>{e(x)}</li>' for x in s['incluye'])
    sen = ''.join(f'<li>{e(x)}</li>' for x in s['senales'])
    faq = ''.join(f'<details{" open" if i == 0 else ""}><summary>{e(q)}{ic("chev",root)}</summary><p>{e(a)}</p></details>' for i, (q, a) in enumerate(s['faq']))
    rel = ''.join(f'<a class="rel-card" href="{root}servicios/{BY_KEY[k]["slug"]}/"><span class="ico">{ic(BY_KEY[k]["icon"],root)}</span><strong>{e(BY_KEY[k]["title"])}</strong><span class="rel-more">Ver servicio {ic("arrow",root)}</span></a>' for k in s['rel'])
    return (head(title, s['meta'], url, root, jsonld(graph)) + '<body class="sv-page" data-root="../../" data-servicio="' + e(s['title']) + '">\n' + header(root) + f'''
<main id="contenido">
<section class="sv-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Migas de pan"><a href="{root}">Inicio</a><span>›</span><a href="{root}servicios/">Servicios</a><span>›</span><span aria-current="page">{e(s["title"])}</span></nav>
    <div class="sv-hero-grid">
      <div>
        <h1>{e(h1)}</h1>
        <p class="lead">{e(s["intro"])}</p>
        <div class="cta-row">
          <a href="#contacto" class="btn btn-lg">Pedir presupuesto gratis {ic("arrow",root)}</a>
          <a href="tel:{PHONE_TEL}" class="btn btn-ghost btn-lg">{ic("phone",root)} 722 115 251</a>
        </div>
        <ul class="trust"><li>{ic("check",root)} Visita a domicilio sin coste</li><li>{ic("check",root)} Presupuesto sin compromiso</li><li>{ic("check",root)} Para particulares, comunidades y empresas</li></ul>
      </div>
      <div class="sv-badge" aria-hidden="true">{ic(s["icon"],root)}</div>
    </div>
  </div>
</section>

<section class="section sv-body">
  <div class="wrap sv-grid">
    <div class="sv-main">
      <h2 id="que-hacemos">Qué hacemos</h2>
      <ul class="checklist">{inc}</ul>

      <h2>Cuándo necesitas este servicio</h2>
      <ul class="checklist soft">{sen}</ul>

      <h2 id="proceso">Cómo trabajamos</h2>
      <ol class="mini-steps">
        <li><b>1</b><strong>Visita sin coste</strong><span>Vamos a tu domicilio, local o edificio para ver el trabajo.</span></li>
        <li><b>2</b><strong>Presupuesto sin compromiso</strong><span>Te lo entregamos con el plan de trabajo y de seguridad.</span></li>
        <li><b>3</b><strong>Ejecución con garantía</strong><span>Trabajamos con las mejores marcas y gestionamos las licencias de obra si se necesitan.</span></li>
      </ol>

      <h2>Preguntas frecuentes</h2>
      <div class="faq">{faq}</div>
    </div>
    <aside class="sv-aside">
      <div class="aside-card">
        <h3>¿Hablamos?</h3>
        <p>Cuéntanos tu caso. Visita y presupuesto sin compromiso en toda la provincia de Valencia.</p>
        <a href="#contacto" class="btn btn-block">Pedir presupuesto</a>
        <a href="tel:{PHONE_TEL}" class="btn btn-ghost-dark btn-block">{ic("phone",root)} {PHONE_TXT}</a>
        <a href="https://wa.me/{WA}?text=Hola%2C%20me%20interesa%3A%20{s["title"].replace(" ","%20")}" class="btn btn-wa btn-block" target="_blank" rel="noopener">{ic("chat",root)} WhatsApp</a>
        <small>Lunes a viernes, de 9:00 a 19:00</small>
      </div>
    </aside>
  </div>
</section>

<section class="section alt sv-rel">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Otros servicios</p><h2>También te puede interesar</h2></div>
    <div class="rel-grid">{rel}</div>
    <p class="more"><a class="link" href="{root}servicios/">Ver los 14 servicios {ic("arrow",root)}</a></p>
  </div>
</section>

''' + contact_section(root, f'Pide tu presupuesto de {s["title"].lower()}', s['title']) + '</main>\n\n' + footer(root))

def hub_page():
    root = '../'
    url = SITE + '/servicios/'
    title = 'Servicios de reparación y reformas en Valencia | Grupo Urbanísima'
    desc = 'Todos los servicios de Grupo Urbanísima en Valencia: tejados, impermeabilización, canalones, fachadas, panel sandwich, chimeneas, reformas y más. Presupuesto gratis.'
    graph = [
      {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Inicio', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Servicios', 'item': url}]},
      {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': s['title'], 'url': f'{SITE}/servicios/{s["slug"]}/'} for i, s in enumerate(SERVICES)]},
    ]
    cards = ''.join(f'''<a class="hub-card" data-slug="{s["key"]}" href="{s["slug"]}/" data-particulares="{s["rank"][0]}" data-comunidades="{s["rank"][1]}" data-empresas="{s["rank"][2]}">
      <span class="ico">{ic(s["icon"],root)}</span><h3>{e(s["title"])}</h3><p>{e(s["short"])}</p><ul class="bits">{"".join("<li>"+e(b)+"</li>" for b in s["bits"])}</ul><span class="rel-more">Ver servicio {ic("arrow",root)}</span></a>''' for s in SERVICES)
    return (head(title, desc, url, root, jsonld(graph)) + '<body class="sv-page" data-root="../">\n' + header(root) + f'''
<main id="contenido">
<section class="sv-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Migas de pan"><a href="{root}">Inicio</a><span>›</span><span aria-current="page">Servicios</span></nav>
    <h1>Servicios en Valencia para particulares, comunidades y empresas</h1>
    <p class="lead">Reparamos e impermeabilizamos tejados, terrazas y cubiertas, y realizamos canalones, fachadas, reformas y mucho más en toda la provincia de Valencia. Todos los servicios están disponibles para cualquier cliente; elige tu perfil y los ordenamos de más a menos solicitados.</p>
    <div class="cta-row"><a href="#contacto" class="btn btn-lg">Pedir presupuesto gratis {ic("arrow",root)}</a><a href="tel:{PHONE_TEL}" class="btn btn-ghost btn-lg">{ic("phone",root)} 722 115 251</a></div>
  </div>
</section>
<section class="section">
  <div class="wrap">
    <div class="tabs" role="tablist" aria-label="Tipo de cliente">
      <button class="tab is-on" role="tab" aria-selected="true" data-filter="all">Todos</button>
      <button class="tab" role="tab" aria-selected="false" data-filter="particulares">{ic("home",root)}Particulares</button>
      <button class="tab" role="tab" aria-selected="false" data-filter="comunidades">{ic("building",root)}Comunidades</button>
      <button class="tab" role="tab" aria-selected="false" data-filter="empresas">{ic("factory",root)}Empresas y naves</button>
    </div>
    <p class="svc-status" id="svc-status" aria-live="polite">Mostrando los 14 servicios</p>
    <div class="hub-grid" id="hub-grid">{cards}</div>
  </div>
</section>
''' + contact_section(root, 'Pide tu presupuesto gratis') + '</main>\n\n' + footer(root))

# ---------------------------------------------------------------- ESCRITURA
def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf8').write(content)

def home_cards():
    out = ''
    for s in SERVICES:
        r = s['rank']
        bits = ''.join(f'<li>{e(b)}</li>' for b in s['bits'])
        out += f'''      <article class="svc" id="svc-{s["key"]}" data-slug="{s["key"]}" data-particulares="{r[0]}" data-comunidades="{r[1]}" data-empresas="{r[2]}">
        <span class="tag">Más solicitado</span>
        <span class="ico"><svg class="i"><use href="#i-{s["icon"]}"/></svg></span>
        <h3><a class="svc-link" href="servicios/{s["slug"]}/">{e(s["title"])}</a></h3>
        <p>{e(s["short"])}</p>
        <ul class="bits">{bits}</ul>
        <div class="svc-actions">
          <a href="#contacto" class="link" data-title="{e(s["title"])}">Pedir presupuesto <svg class="i"><use href="#i-arrow"/></svg></a>
          <a class="more-link" href="servicios/{s["slug"]}/">Ver servicio</a>
        </div>
      </article>
'''
    return out

def home_problems():
    tiles = ''.join(f'''
      <a class="prob" href="servicios/{BY_KEY[k]["slug"]}/"><span class="ico"><svg class="i"><use href="#i-{icn}"/></svg></span><span class="prob-t"><strong>{e(t)}</strong><small>{e(sub)}</small></span><svg class="i go"><use href="#i-arrow"/></svg></a>''' for icn, t, sub, k in PROBLEMS)
    return f'''<!-- PROBLEMAS-START -->
<section class="section alt problems" id="problemas">
  <div class="wrap">
    <div class="head">
      <p class="eyebrow">Elige tu caso</p>
      <h2>¿Qué necesitas resolver?</h2>
      <p class="sub">Pulsa el que más se parezca a tu problema. Te llevamos al servicio adecuado, con presupuesto gratis y sin compromiso.</p>
    </div>
    <div class="prob-grid">{tiles}
    </div>
    <p class="prob-help">¿No ves tu caso? <a href="tel:{PHONE_TEL}">Llámanos al {PHONE_TXT}</a> o <a href="https://wa.me/{WA}?text=Hola%2C%20quiero%20pedir%20presupuesto" target="_blank" rel="noopener">escríbenos por WhatsApp</a>.</p>
  </div>
</section>
<!-- PROBLEMAS-END -->

'''

def patch_home():
    path = os.path.join(ROOT, 'index.html')
    s = open(path, encoding='utf8').read()
    a = s.index('<div class="svc-grid" id="service-grid" data-cat="all">') + len('<div class="svc-grid" id="service-grid" data-cat="all">')
    b = s.index('    </div>\n    <p class="more">', a)
    s = s[:a] + '\n' + home_cards() + s[b:]
    if '<!-- PROBLEMAS-START -->' in s:
        i = s.index('<!-- PROBLEMAS-START -->'); j = s.index('<!-- PROBLEMAS-END -->') + len('<!-- PROBLEMAS-END -->\n\n')
        s = s[:i] + home_problems() + s[j:]
    else:
        s = s.replace('<!-- SERVICIOS -->', home_problems() + '<!-- SERVICIOS -->', 1)
    open(path, 'w', encoding='utf8').write(s)

def build():
    patch_home()
    write('servicios/index.html', hub_page())
    for s in SERVICES:
        write(f'servicios/{s["slug"]}/index.html', service_page(s))

    # sitemap
    urls = [(SITE + '/', '1.0', 'monthly'), (SITE + '/servicios/', '0.9', 'monthly')]
    urls += [(f'{SITE}/servicios/{s["slug"]}/', '0.8', 'monthly') for s in SERVICES]
    urls += [(f'{SITE}/{p}/', '0.2', None) for p in ('aviso-legal', 'ley-proteccion-datos', 'aviso-ley-cookies', 'condiciones')]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u, pr, cf in urls:
        sm += f'  <url><loc>{u}</loc>' + (f'<changefreq>{cf}</changefreq>' if cf else '') + f'<priority>{pr}</priority></url>\n'
    write('sitemap.xml', sm + '</urlset>\n')

    # .htaccess: se conserva todo y se regeneran solo las redirecciones
    ht = open(os.path.join(ROOT, '.htaccess'), encoding='utf8').read()
    a = ht.index('# --- URLs antiguas'); b = ht.index('# --- Archivos antiguos')
    rules = ('# --- URLs antiguas -> web nueva (generado por scripts/build-services.py).\n'
             '#     QSA conserva los parámetros originales (gclid, utm_*): imprescindible para no perder la atribución de Google Ads.\n')
    allr = []
    for key, olds in OLD.items():
        for o in olds: allr.append((o, f'/servicios/{BY_KEY[key]["slug"]}/'))
    allr += list(OTHER_REDIRECTS.items()) + [(o, '/') for o in OLD_AC]
    for o, d in sorted(allr): rules += f'RewriteRule ^{o}/?$ {d} [R=301,L,QSA]\n'
    write('.htaccess', ht[:a] + rules + '\n' + ht[b:])
    return allr

if __name__ == '__main__':
    r = build()
    print(f'{len(SERVICES)} páginas de servicio + hub, sitemap y {len(r)} redirecciones generados.')
