from database import select, insert, update, delete


class ContainerDB:
    @select
    def get_containers_by_project(project):
        query = """
        SELECT name, description FROM (container AS c
            INNER JOIN container_info AS ci
            ON c.id=ci.container_id
        ) WHERE project_id = (
            SELECT id FROM project
            WHERE name=%s
        );
        """
        arg = (project,)

        return query, arg

    def get_info_by_name(name):
        @select
        def q1(*args):
            query = """
            SELECT name, description, gpu FROM (container AS c
                INNER JOIN container_info AS ci
                ON c.id=ci.container_id
            ) WHERE name=%s
            """
            return query, args
        @select
        def q2(*args):
            query = """
            SELECT port FROM container_ports
            WHERE container_id=(
                SELECT id FROM container
                WHERE name=%s
            )
            """
            return query, args
        @select
        def q3(*args):
            query = """
            SELECT k, v FROM container_envs
            WHERE container_id=(
                SELECT id FROM container
                WHERE name=%s
            )
            """
            return query, args
        
        info = q1(name)[0]
        info["ports"] = [x["port"] for x in q2(name)]
        info["envs"] = {x["k"]: x["v"] for x in q3(name)}

        return info

    def insert_container(name, project, description, gpu, ports, envs, os, frameworks, ip_addr):
        # Add container
        @insert
        def q1(*args):
            query = """
            INSERT INTO container(project_id, name)
            VALUES (
                (SELECT id FROM project WHERE name=%s),
                %s
            );
            """
            return query, args

        # Add container info
        @insert
        def q2(*args):
            query = """
            INSERT INTO container_info(container_id, description, gpu, ip)
            VALUES (
                (SELECT id FROM container WHERE name=%s),
                %s,
                %s,
                %s
            );
            """
            return query, args

        # Add ports of container
        @insert
        def q3(*args):
            query = """
            INSERT INTO container_ports(container_id, port)
            VALUES (
                (SELECT id FROM container WHERE name=%s),
                %s
            );
            """
            return query, args

        # Add envs of container
        @insert
        def q4(*args):
            query = """
            INSERT INTO container_envs(container_id, k, v)
            VALUES (
                (SELECT id FROM container WHERE name=%s),
                %s,
                %s
            );
            """
            return query, args

        # Add os of container
        @insert
        def q5(*args):
            query = """
            INSERT INTO container_os(container_id, version_id)
            VALUES (
                (SELECT id FROM container WHERE name=%s),
                (SELECT ov.id FROM os_version AS ov
                    INNER JOIN os AS o
                    ON ov.os_id=o.id 
                    WHERE name=%s AND version=%s
                )
            );
            """
            return query, args

        # Add envs of container
        @insert
        def q6(*args):
            query = """
            INSERT INTO container_framework(container_id, version_id)
            VALUES (
                (SELECT id FROM container WHERE name=%s),
                (SELECT fv.id FROM framework_version AS fv
                    INNER JOIN framework AS f
                    ON fv.framework_id=f.id 
                    WHERE name=%s AND version=%s
                )
            );
            """
            return query, args

        q1(project, name)
        q2(name, description, gpu, ip_addr)

        for port in ports:
            q3(name, port)

        for k, v in envs.items():
            q4(name, k, v)

        q5(name, os["name"], os["version"])

        for framework in frameworks:
            q6(name, framework["name"], framework["version"])

    def update_container_by_name(old_name, new_name, description, gpu, ports, envs):
        # Modify container
        @update
        def q1(*args):
            query = """
            UPDATE container
            SET name=%s
            WHERE name=%s
            """
            return query, args

        # Modify container info
        @update
        def q2(*args):
            query = """
            UPDATE container_info
            SET
                description=%s,
                gpu=%s
            WHERE container_id=(SELECT id FROM container WHERE name=%s)
            """
            return query, args

        @update
        def q3(*args):
            query = """
            INSERT INTO container_ports(container_id, port)
            VALUES (
                (SELECT id FROM container WHERE name=%s),
                %s
            );
            """
            return query, args

        @update
        def q4(*args):
            query = """
            INSERT INTO container_envs(container_id, k, v)
            VALUES (
                (SELECT id FROM container WHERE name=%s),
                %s,
                %s
            );
            """
            return query, args

        q1(new_name, old_name)
        q2(description, gpu, new_name)

        for port in ports:
            q3(new_name, port)

        for k, v in envs.items():
            q4(new_name, k, v)

    @update
    def update_ip_by_name(name, ip_addr):
        query = """
        UPDATE container_info
        SET ip=%s
        WHERE container_id=(
            SELECT id FROM container
            WHERE name=%s
        );
        """
        arg = (ip_addr, name)
        return query, arg

    @delete
    def delete_by_name(name):
        query = """
        DELETE FROM container
        WHERE name=%s
        """
        arg = (name,)
        return query, arg
